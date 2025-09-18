import fireducks.pandas as pd

# Diccionario para la función get_top_building_blocks
get_top_building_blocks_dict = {
    "description": """Obtiene un DataFrame pivotado con valores mensuales por building blocks (conceptos).
    Utiliza por defecto los filtros: TIPO_FILTRO='GPS', CATEGORIA='DAIRY', MARCA existente y no 'HERSHEY's', NOMBRE_ETIQUETA contiene 'REAL|GPS'.
    Si el usuario no pide explícitamente 
    Esta función se puede utilizar directamente como bb_importance = get_top_building_blocks(df) y regresa el dataframe en bb_importance[0]
    Permite filtrado adicional por año, nombre de etiqueta y campo personalizado.
    Se utiliza cuando el usuario quiere analizar la importancia relativa de diferentes conceptos (building blocks) por mes.
    El usuario puede mencionar 'Quiero ver los building blocks más importantes', 'Análisis de building blocks por mes' o algo similar.""",
    "parameters": {
        "df": {
            "type": "pd.DataFrame",
            "description": "DataFrame de entrada con los datos en bruto",
            "required": True
        },
        "anio": {
            "type": "int",
            "description": "Año para filtrar los datos",
            "required": False,
            "default": None
        },
        "nombre_etiqueta": {
            "type": "str",
            "description": "Nombre de la etiqueta para filtrar (REAL o GPS)",
            "required": False,
            "default": None
        },
        "by_column": {
            "type": "str",
            "description": "Columna adicional para filtrar los datos",
            "required": False,
            "default": None
        },
        "by_value": {
            "type": "str",
            "description": "Valor para filtrar en la columna adicional",
            "required": False,
            "default": None
        }
    },
    "returns": {
        "type": "pd.DataFrame",
        "description": """DataFrame pivotado con meses como columnas y building blocks (años, etiquetas, conceptos) como filas. 
        Los valores representan la suma por mes para cada building block."""
    }
}

def get_top_building_blocks(df, anio=None, nombre_etiqueta=None, by_column=None, by_value=None):
    """
    Parameters:
    -----------
    df : pandas DataFrame
        Input dataframe with the raw data
    anio : int, list or None, default=None
        Year or list of years to filter by
    nombre_etiqueta : str, default=None
        Name of the label to filter by
    by_column : str, default=None
        Column to filter by (optional)
    by_value : str, default=None
        Value to filter by in the specified column (optional)
    """
    # Validar que ambos parámetros by_column y by_value sean proporcionados o ninguno de los dos
    if (by_column is not None and by_value is None) or (by_column is None and by_value is not None):
        raise ValueError("Ambos parámetros by_column y by_value deben ser proporcionados o ninguno de los dos.")
    
    df_copy = df.copy()
    # df_copy["NOMBRE_ETIQUETA"] = df_copy["ETIQUETA"].str.split(" ", n=1).str[0]
    df_copy["FECHA_"] = pd.to_datetime(df_copy["FECHA"], format="%d/%m/%Y", errors='coerce')
    # df_copy["MES_ANO"] = df_copy["FECHA_"].dt.strftime('%b-%Y')
    meses_es = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    df_copy["MES_ANO"] = df_copy["FECHA_"].dt.month.map(meses_es) + '-' + df_copy["FECHA_"].dt.year.astype(str)
    # Construir el filtro base
    filtros = [
        (df_copy.TIPO_FILTRO == 'GPS'),
        (df_copy.CATEGORIA == 'DAIRY'),
        (df_copy.MARCA.notnull()),
        (df_copy.MARCA != "HERSHEY's"),
        (df_copy.NOMBRE_ETIQUETA.str.contains('REAL|GPS', na=False))
    ]
    
    # Filtro para año(s)
    if anio is not None:
        if isinstance(anio, list):
            # Si es una lista de años, usar operador isin
            filtros.append(df_copy["AÑO"].isin(anio))
        else:
            # Si es un solo año, usar igualdad
            filtros.append(df_copy["AÑO"] == anio)
    
    # Filtro para etiqueta
    if nombre_etiqueta is not None:
        filtros.append(df_copy.NOMBRE_ETIQUETA == nombre_etiqueta)
    
    # Filtro por columna y valor específicos
    if by_column is not None and by_value is not None:
        filtros.append(df_copy[by_column].str.contains(by_value, na=False))
    # Aplicar todos los filtros combinados con AND
    df_filtered = df_copy[pd.Series(True, index=df_copy.index)]
    for filtro in filtros:
        df_filtered = df_filtered[filtro]
    
    # Verificar si hay datos después de filtrar
    if df_filtered.empty:
        print("No hay datos que cumplan con los filtros especificados.")
        return None
    
    # Crear el df_pivot_actividad agrupando por actividad
    temp_df_actividad = df_filtered.groupby(["NOMBRE_ETIQUETA", "ETIQUETA", "AÑO", "CONCEPTO", "ACTIVIDAD"])['VALOR'].sum().reset_index()
    
    # Obtener el top 3 de actividades por la suma de VALOR para cada combinación de NOMBRE_ETIQUETA, AÑO y CONCEPTO
    df_pivot_actividad = pd.DataFrame()
    
    # Agrupar por las columnas de interés para encontrar el top 3 en cada grupo
    for (etiqueta, ano, concepto), group_data in temp_df_actividad.groupby(["NOMBRE_ETIQUETA", "AÑO", "CONCEPTO"]):
        # Ordenar por VALOR en orden descendente y tomar los 3 primeros
        top3 = group_data.sort_values(by='VALOR', ascending=False).head(3)
        # Añadir al DataFrame resultante
        df_pivot_actividad = pd.concat([df_pivot_actividad, top3], ignore_index=True)
    
    # Group by the specified column and calculate the sum of VALOR
    df_grouped = df_filtered.groupby(["NOMBRE_ETIQUETA", "ETIQUETA", "AÑO", "CONCEPTO"])['VALOR'].sum().reset_index()
    df_grouped = df_grouped.drop(columns=["ETIQUETA"])
    
    # Asegurarse de que la columna AÑO sea de tipo string antes de hacer pivot
    df_grouped["AÑO"] = df_grouped["AÑO"].astype(str)
    
    df_pivot = df_grouped.pivot(index=["NOMBRE_ETIQUETA", "CONCEPTO"], columns="AÑO", values="VALOR")
    
    # Asegurarse de que los nombres de columnas son todos strings
    df_pivot.columns = df_pivot.columns.astype(str)
    
    df_pivot = df_pivot.reset_index()
    
    return [df_pivot_actividad, df_pivot]

# Diccionario para la función generate_heatmap
crear_grafico_cascada_dict = {
    "description": """Crea un gráfico de cascada (waterfall graph) para visualizar la importancia de los building blocks.
    Se utiliza para mostrar gráficamente los resultados de la función get_top_building_blocks. 
    Esta función se puede utilizar directamente como bb_importance = get_top_building_blocks(df) y luego crear el mapa de calor con crear_grafico_cascada(bb_importance[1]).
    El usuario puede mencionar 'Quiero ver la importancia de los building blocks', 'Visualiza los building blocks' o algo similar.
    No utilices estilos de seaborn, utiliza el estilo de matplotlib por defecto.""",
    "parameters": {
        "bb_importance": {
            "type": "pd.DataFrame",
            "description": "DataFrame pivotado con la información de building blocks por mes (output de get_top_building_blocks)",
            "required": True
        }
    },
    "returns": {
        "type": "matplotlib.figure.Figure",
        "description": "Objeto de figura de matplotlib con el mapa de calor de building blocks por mes"
    }
}

def crear_grafico_cascada(df):
    """
    Crea un gráfico de cascada a partir de un DataFrame con los valores por concepto y año,
    donde los totales y años están conectados en cascada. Ignora valores NaN.
    
    Parameters:
    -----------
    df : pandas DataFrame
        DataFrame con los datos. Debe contener una columna 'CONCEPTO' y columnas para cada año.
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Objeto figura de matplotlib.
    """

    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    color_positivo = '#2ecc71'  # Verde más suave
    color_negativo = '#e74c3c'  # Rojo más suave
    color_total = '#3498db'     # Azul más suave
    width=0.6

    # Hacer una copia del DataFrame para no modificar el original
    df_clean = df.copy()
    
    # Detectar automáticamente las columnas de valores (años)
    columnas_no_valores = ['CONCEPTO', 'NOMBRE_ETIQUETA', 'AÑO']
    columnas_valores = [col for col in df_clean.columns if col not in columnas_no_valores]
    
    # Ordenar las columnas de valores en caso de que sean años
    columnas_valores = sorted(columnas_valores)
    if len(columnas_valores) > 1:
        titulo=f"Gráfico de Cascada de los años {columnas_valores}"
    else:
        titulo=f"Gráfico de Cascada del año {columnas_valores[0]}"
    
    # Calcular el número total de barras
    num_conceptos = len(df_clean)
    num_years = len(columnas_valores)
    total_barras = num_conceptos * num_years + num_years  # conceptos + totales
    
    # Calcular dimensiones del gráfico basadas en el número de barras
    width_per_bar = 0.8  # Espacio horizontal por barra en pulgadas
    height_factor = 0.2  # Factor de altura por barra
    
    # Calcular tamaño mínimo de la figura
    min_width = 8
    min_height = 6
    
    # Calcular tamaño según cantidad de barras
    fig_width = max(min_width, total_barras * width_per_bar)
    fig_height = max(min_height, num_conceptos * height_factor * 6)
    
    # Crear figura y ejes con tamaño dinámico
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Preparar listas para el gráfico
    etiquetas = []
    posiciones_x = []
    alturas_y = []
    
    # Base global para mantener el efecto de cascada entre años
    base_global = 0
    
    # Calcular alturas y bases para cada año
    for i, anio in enumerate(columnas_valores):
        # Procesar cada año por separado
        datos_anio = df_clean[anio].copy()
        conceptos = df_clean['CONCEPTO'].tolist()
        
        # Añadir barras para este año
        base_anio = base_global  # La base inicial del año es donde terminó el año anterior
        
        # Primero los conceptos individuales
        for j, (concepto, valor) in enumerate(zip(conceptos, datos_anio)):
            # Ignorar valores NaN
            if pd.isna(valor) or valor == 0:
                continue
                
            # Convertir a float para operaciones numéricas
            valor = float(valor)
            
            # Añadir etiqueta
            etiqueta = f"{concepto}\n{anio}"
            etiquetas.append(etiqueta)
            
            # Guardar posición x y altura final para las líneas punteadas
            posiciones_x.append(len(etiquetas)-1)
            alturas_y.append(base_anio + valor)
            
            # Determinar color según el valor
            color = color_positivo if valor >= 0 else color_negativo
            
            # Crear la barra con su base correspondiente
            rect = ax.bar(len(etiquetas)-1, valor, width, bottom=base_anio, 
                         color=color, edgecolor='black', linewidth=0.5)
            
            # Añadir valor encima de la barra
            if valor > 0:
                texto_y = base_anio + valor + abs(valor) * 0.05  # 5% por encima para positivos
            else:
                texto_y = base_anio + valor - abs(valor) * 0.05  # 5% por debajo para negativos
            
            ax.text(len(etiquetas)-1, texto_y, f"{valor:,.0f}", 
                   ha='center', 
                   va='bottom' if valor > 0 else 'top', 
                   fontsize=8, 
                   color='black', 
                   fontweight='bold')
            
            # Actualizar la base para la siguiente barra
            base_anio += valor
        
        # Añadir el total del año como una barra independiente
        etiqueta = f"Total {anio}"
        etiquetas.append(etiqueta)
        
        # El total es la suma de todos los valores del año (ignorando NaN)
        total = datos_anio.dropna().sum()
        
        # La base del total es 0 si es el primer año, o la base global si no
        base_total = 0 if i == 0 else base_global
        
        # Guardar posición x y altura final para las líneas punteadas
        posiciones_x.append(len(etiquetas)-1)
        alturas_y.append(base_total + total)
        
        # Crear barra del total
        rect = ax.bar(len(etiquetas)-1, total, width, bottom=base_total,
                     color=color_total, edgecolor='black', linewidth=0.5)
        
        # Añadir valor encima de la barra del total (en lugar de en el centro)
        texto_y_total = base_total + total + abs(total) * 0.05
        ax.text(len(etiquetas)-1, texto_y_total, f"{total:,.0f}", 
               ha='center', 
               va='bottom', 
               fontsize=8, 
               color='black',  # Cambiado a negro para mejor visibilidad
               fontweight='bold')
        
        # Actualizar la base global para el próximo año
        base_global = base_total + total
    
    # Verificar si hay elementos para dibujar líneas punteadas
    if len(posiciones_x) > 1:
        # Añadir líneas punteadas que conecten las barras
        for i in range(len(posiciones_x)-1):
            # Calcular posiciones para la línea
            x1 = posiciones_x[i] + width/2
            y1 = alturas_y[i]
            x2 = posiciones_x[i+1] - width/2
            y2 = alturas_y[i]  # Misma altura para línea horizontal
            
            # Dibujar línea punteada horizontal
            ax.plot([x1, x2], [y1, y2], 'k--', alpha=0.5, linewidth=1)
            
            # Si hay cambio de nivel, dibujar línea vertical
            if abs(alturas_y[i] - alturas_y[i+1]) > 1:  # Umbral para evitar líneas innecesarias
                ax.plot([x2, x2], [y1, alturas_y[i+1]], 'k--', alpha=0.5, linewidth=1)
    
    # Configurar etiquetas del eje X
    ax.set_xticks(range(len(etiquetas)))
    ax.set_xticklabels(etiquetas, rotation=45, ha='right', fontsize=9)
    
    # Configurar formato de los números en el eje Y con separadores de miles
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    # Eliminar bordes del gráfico
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_alpha(0.3)
    ax.spines['bottom'].set_alpha(0.3)
    
    # Configurar título y ejes
    ax.set_title(titulo, fontsize=14, pad=20)
    ax.set_ylabel('Valor', fontsize=12)
    
    # Quitar el grid completamente
    ax.grid(False)
    
    # Añadir línea de cero
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Ajustar el tamaño y los márgenes
    plt.tight_layout()
    
    return fig

