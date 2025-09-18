import re
from typing import Dict, List, Tuple, Union, AsyncGenerator, Optional
import asyncio
from core.logger import logger
from langchain_core.messages import HumanMessage, SystemMessage
from services.speech.speech import text_to_speech
from services.DataAnalysisFlow.DataAnalyst import DataAnalysisFlow
from services.DataAnalysisFlow.tools.tools_for_bi_danone import get_all_paired_tools
from services.DataAnalysisFlow.providers.azure_provider import AzureOpenAIProvider
from services.DataAnalysisFlow.utils.streaming_handlers import StreamHandler
from templates.system_prompts import receiving_system_prompt, interpretation_system_prompt, direct_answer_system_prompt
from services.chat.memory import memory_service
from services.chat.messages import send_message
from .messages import create_message
from services.temporal_memory.storage import store_image, store_data
from core.config import settings

# Initialize stream handler
stream_handler = StreamHandler()
additional_context_for_bi_danone = """
    Para estos ejercicios en particular, vamos a apegarnos a un formato que prefiere el cliente.
    1. para tablas que muestran datos mensuales, deberás usar los meses como columnas y las filas corresponderán a la serie en cuestión.
        Y siempre deberás ordenar los meses en forma cronológica; por defecto los meses estarán en orden alfabético, en español y en mayúscula (ENE, FEB, MAR, ABR, MAY, JUN, JUL, AGO, SEP, OCT, NOV, DIC).
    2. Del mismo modo, para visualizaciones que involucren series mensuales, los meses deberán ordenarse en el eje x ascendentemente, y las series en el eje y.
    3. Para tablas mensuales que involucren más de una serie, pivotea la tabla para que las series correspondan a filas, y los meses correspondan a columnas.
    4. Para visualizaciones que impliquen mostrar muchos elementos (por ejemplo SKU, categorías muy diversas, etc.), muestra únicamente los 10 elementos más importantes, y el resto de los elementos en una categoría "Otros".
    5. Si el usuario pide estadísticas descriptivas (como crecimiento de SKU, evolución mensual, etc.), usa por defecto el filtro df.NOMBRE_ETIQUETA.str.contains('REAL', na=False) para obtener los datos reales, y df.NOMBRE_ETIQUETA.str.contains('GPS', na=False) para obtener las predicciones generadas por el sistema gps.


    Para los datos de este ejercicio, algunas columnas importantes son:

    - ETIQUETA: que etiqueta datos reales y predicciones. Existen seis etiquetas: 
        * ['REAL 2022', 'REAL 2023', 'REAL 2024'] (los datos reales en 2022, 2023, 2024)
        * ['GPS 2022', 'GPS 2023', 'GPS 2024'] (las predicciones generadas por el sistema gps en 2022, 2023, 2024)
    
    Terminología del cliente:
    - "estacionalidad histórica" | se refiere la variación porcentual de un mes con respecto al anterior inmediato, es decir, valor_mes_actual/valor_mes_anterior - 1.
    - "bb" | se refiere a los building blocks, que son una categoría de iniciativas que se pueden incluir en el análisis.
    - "inno" | se refiere a las iniciativas de innovación, que son otra categoría de iniciativas que se pueden incluir en el análisis.
    - "gps" | se refiere a las predicciones generadas por el sistema gps, que son una categoría de iniciativas que se pueden incluir en el análisis.
    - "opps" | se refiere a una categoría de iniciativas. Las OPPS se pueden encontrar en la columna actividad mediante df.ACTIVIDAD.str.contains('OPPS', na=False).
"""

# Initialize Azure OpenAI provider for DataAnalyst
azure_provider = AzureOpenAIProvider(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
    model=settings.AZURE_OPENAI_MODEL,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    temperature=0.3
)

# Initialize DataAnalysisFlow
data_analysis = DataAnalysisFlow(
    llm_provider=azure_provider,
    data_directory=settings.DATA_ANALYSIS_DIRECTORY,
    stream_results=True,
    progress_callback=stream_handler.stream_handler,
    style_config={
            "color_palette": [
                # Azules originales y derivados
                "#324BAA", "#11ACED", "#89C8F2", "#5BB5E9", "#4CABE4",
                "#1E3F8A", "#A3D9F9", "#E6F5FD",

                # Fucsias / Rosas intensos
                "#F72585", "#FF4FA0", "#FF9EC9", "#D61C88",

                # Verdes tipo aqua / menta
                "#2ED9C3", "#54E1C2", "#B3F4EB", "#0FC2C0",

                # Rojos
                "#F44336", "#E53935", "#FF6B6B", "#B71C1C"
            ],
        },
    logger=logger,
    # custom_functions=[
    #     {
    #         'function': tuple_[1],
    #         'description': tuple_[0]['description'],
    #         'parameters': tuple_[0]['parameters'],
    #         'returns': tuple_[0]['returns']
    #     } 
    #     for tuple_ in get_all_paired_tools()
    #  ],
)


interpretation_system_prompt += "\n\n" + additional_context_for_bi_danone + "\n\n Aquí tienes una descripción de los datos con los que se están trabajando" + data_analysis.available_datasets.__str__()
# Keywords that might indicate a data analysis question
DATA_ANALYSIS_KEYWORDS = [
    r'(?:cuántas?|cuantas?)\s+(?:columnas?|filas?)',
    r'dataset',
    r'base\s+de\s+datos',
    r'datos',
    r'analiz[a-z]+',
    r'calcul[a-z]+',
    r'estadístic[a-z]+',
    r'promedio',
    r'media',
    r'máximo',
    r'mínimo',
    r'total',
    r'suma',
    r'conteo',
    r'gr[aá]fic[oa]',
    r'visualiz[a-z]+',
    r'facturación',
    r'ventas?',
    r'finanz[a-z]+',
    r'report[e|ar]',
    r'tendencia',
    r'predicción',
    r'proyección',
    r'comparación',
    r'forecast',
    r'analiz[a-z]+',
    r'valores?\s+atípicos',
    r'valores?\s+positivo[s]?',
    r'valores?\s+negativo[s]?',
    r'result[a-z]+',
    r'resultad[oa][s]?',
    r'resultante[s]?',
    r'SKU[s]?',
    r'sku[s]?',
    r'producto[s]?',
    r'categoría[s]?',
    r'categorías?',
    # r'BB[s]?', r'bb[s]?',
    # r'building block[s]?',
    # r'building blocks?',
    # r'BUILDING BLOCKS?',
    # r'BUILDING BLOCKS',
    # r'q/h',
    # r'Q/H',
    # r'IF/PF',
    r'estacionalidad',
    # r'inno[s]?',
    # r'INNO[s]?',
    # r' q ',
    # r'gps', r'GPS',
    r'combinaci[ó|o]n[es]?',
    r'retenci[ó|o]n',
    r'rentables?',r'rentabilidad',
    r'varía', r'variación',
    r'variaciones?',
    r'variabilidad',
    r'variables',
    r'datasets?',
    r'base de datos',
    r'potencial de crecimiento',
    r'crecimiento',
    r'segmentos de clientes',
    r'valor de vida útil',
    r'Cómo influyen los tipos de contrato en la retención',
    r'comportamiento de compra por ubicación geográfica'
]

async def is_data_analysis_question(question: str) -> bool:
    """Determine if a question requires data analysis
    
    Args:
        question (str): The user's question
        
    Returns:
        bool: True if the question likely requires data analysis
    """
    # Convert to lowercase for case-insensitive matching
    question_lower = question.lower()
    
    # Check if any of the keywords are in the question
    for keyword_pattern in DATA_ANALYSIS_KEYWORDS:
        if re.search(keyword_pattern, question_lower):
            return True
    
    return False

async def process_user_message(session_id: str, message: str) -> AsyncGenerator[str, None]:
    """Process a user message and generate a response
    
    Args:
        session_id (str): Unique identifier for the conversation
        message (str): The user's message
        
    Yields:
        Tokens of the response as they are generated
    """
    # Add the user message to memory
    memory_service.add_message(session_id, "user", message)
    
    # Determine if this is a data analysis question
    is_data_analysis = await is_data_analysis_question(message)
    
    # Get an initial explanation of what will be done
    full_response = "# Inicia respuesta del asistente\n\n"
    # Yield the explanation token by token
    if is_data_analysis:
        # Make message for data analysis
        messages = [
            SystemMessage(content=receiving_system_prompt),
            HumanMessage(content=message)
        ]
        full_response += "### Respuesta introductoria del asistente:\n\n"
        async for token in send_message(messages):
            full_response += token
            yield create_message("text", text=token)
        full_response += "\n\n"
        yield {"type": "break_of_message"}  # Add a line break after the explanation message
        
        # Use DataAnalysisFlow
        data_analysis_response = ""
        last_progress_percentage = 0
        planning_text = ""
        code_text = ""
        
        async for chunk in await data_analysis.process_question(message, additional_context=additional_context_for_bi_danone):
            if isinstance(chunk, dict):
                chunk_type = chunk.get("type", "text")
                progress = chunk.get("content",{}).get("progress", 0)
                message_text = chunk.get("content",{}).get("message", "")
                result = chunk.get("content",{}).get("result", {})

                if chunk_type == "planning_token":
                    token = chunk.get("content", {}).get("text", "")
                    planning_text += token
                    # Create special backend process message for planning
                    yield create_message(
                        "planning_token", 
                        text=token,
                        metadata={"process_type": "planning"}
                    )
                    continue
                
                # Special handling for code tokens
                elif chunk_type == "code_token":
                    token = chunk.get("content", {}).get("text", "")
                    code_text += token
                    # Create special backend process message for code generation
                    yield create_message(
                        "code_token", 
                        text=token,
                        metadata={"process_type": "code_generation"}
                    )
                    continue
                
                # Handle planning start/complete
                elif chunk_type in ["planning_start", "planning_complete"]:
                    # text = chunk.get("content", {}).get("text", "")
                    
                    yield chunk
                    # data_analysis_response += text + "\n"
                    # full_response += text + "\n"
                    continue
                
                # Handle code generation start/complete
                elif chunk_type in ["code_generation_start", "code_generation_complete"]:
                    #text = chunk.get("content", {}).get("text", "")
                    
                    # yield create_message(
                    #     "progress",
                    #     text=text,
                    #     progress=50
                    # )
                    yield chunk
                    # data_analysis_response += text + "\n"
                    # full_response += text + "\n"
                    continue
                elif chunk_type == "progress":
                    progress = chunk.get("content", {}).get("progress", 0)
                    text = chunk.get("content", {}).get("text", "")
                    
                    # Only send significant progress updates (>5% change)
                    is_significant_progress = (progress - last_progress_percentage >= 5) or progress == 100
                    
                    if is_significant_progress or (text and text.strip()): 
                        # Send progress updates for significant progress changes or when there's a message
                        progress_message = create_message(
                            "progress",
                            text=text or "",
                            progress=progress,
                        )
                        yield progress_message
                        
                        # Only send break for meaningful message changes
                        if text and text.strip():
                            yield {"type": "break_of_message"}
                        
                        # Update text accumulation
                        # data_analysis_response += text + "\n"
                        # full_response += text + "\n"
                        
                        # Update last progress percentage
                        last_progress_percentage = progress

                is_significant_progress = (progress - last_progress_percentage >= 5) or progress == 100
                
                if progress == 100:
                    # Process and store images if present
                    image_ids = []
                    if result.get("images") and len(result.get("images", [])) > 0:
                        for i, img_data in enumerate(result.get("images", [])):
                            try:
                                image_id = store_image(img_data, f"analysis_{session_id}")
                                image_ids.append(image_id)
                            except Exception as e:
                                logger.error(f"Error storing image {i}: {str(e)}")
                    
                    # Process and store data if present
                    data_id = None
                    if result.get("data"):
                        try:
                            data_id = store_data(result["data"], f"analysis_{session_id}")
                        except Exception as e:
                            logger.error(f"Error storing data: {str(e)}")
                    
                    # Create the completion message with reference IDs instead of raw data
                    completion_message = create_message(
                        "completion",
                        text=result.get("text", ""),
                        progress=100,
                    )
                    
                    full_response += "\n\n### Respuesta en texto del analizador de datos:\n\n"
                    full_response += result.get("text", "")
                    full_response += "\n\n"

                    # Add asset references if we have any
                    if image_ids or data_id:
                        asset_info = {}
                        if image_ids:
                            asset_info["image_ids"] = image_ids
                        if data_id:
                            asset_info["data_id"] = data_id
                        
                        # Add asset references to the message
                        if "content" not in completion_message:
                            completion_message["content"] = {}
                        completion_message["content"]["asset_refs"] = asset_info
                    
                    # Send the completion message
                    yield completion_message
                    yield {"type": "break_of_message"}
                    
                    # If there are data or images, make the interpretation message
                    if result.get("data") or result.get("images"):
                        content_list = []
                        if result.get("text"):
                            content_list.append({
                                "type": "text",
                                "text": f"Esta es la respuesta en texto del analizador de datos: {result['text']}"
                            })
                        
                        if result.get("data") and len(str(result['data'])) < 5000:
                            content_list.append({
                                "type": "text",
                                "text": f"Estos son los datos que devolvió el analizador de datos:\n\n {result['data']}"
                            })
                            content_list.append({
                                "type": "text",
                                "text": f"Esta fue la pregunta que hizo el usuario: {message}"
                            })
                        
                        images = result.get("images", [])
                        if images:
                            content_list.extend({"type": "image_url", "image_url": {"url":image}} for image in images)

                        messages = [
                            SystemMessage(content=interpretation_system_prompt),
                            HumanMessage(content=content_list)
                        ]
                        full_response += "### Respuesta final (con interpretación de resultados) del analizador de datos:\n\n"
                        async for token in send_message(messages, deployment_name='gpt-4o-voiceanalytics', model='gpt-4o'):
                            full_response += token
                            yield create_message("text", text=token)
                        full_response += "\n\n### Fin de la respuesta del analizador de datos.\n\n"

                    # data_analysis_response += result.get("text", "")
                    # full_response += result.get("text", "")
                    
                elif is_significant_progress or (message_text and message_text.strip()): 
                    # Send progress updates for significant progress changes or when there's a message
                    progress_message = create_message(
                        "progress",
                        text=message_text or result.get("text", ""),
                        progress=progress,
                    )
                    yield progress_message
                    
                    # Only send break for meaningful message changes
                    if message_text and message_text.strip():
                        yield {"type": "break_of_message"}
                    
                    # Update text accumulation
                    # data_analysis_response += message_text or result.get("text", "")
                    # full_response += message_text or result.get("text", "")
                    
                    # Update last progress percentage
                    last_progress_percentage = progress
            elif isinstance(chunk, str) and chunk.strip():
                # Direct string output - only process non-empty strings
                chunk_message = create_message(
                    "text",
                    text=chunk,
                )
                yield chunk_message
                # full_response += chunk
    else:
        # Use regular chat model with conversation history
        history = memory_service.format_for_llm(session_id)
        
        # Prepare the messages for the LLM
        chat_messages = [
            {"role": "system", "content": "Eres un asistente útil. Responde a la pregunta del usuario basándote en el historial de la conversación."}
        ]
        chat_messages.extend(history)
        
        # Send the message to the LLM
        async for token in send_message(chat_messages):
            yield create_message("text", text=token)
            # Append the token to the full response
            full_response += token
    
    # Add the assistant's message to memory
    memory_service.add_message(session_id, "assistant", full_response)
    
    # Ensure we always send a final completion message with 100% progress
    # This ensures the progress bar will always reach 100%
    if is_data_analysis:
        # Create a summary completion message
        final_message = create_message(
            "completion",
            progress=100
        )
        yield final_message