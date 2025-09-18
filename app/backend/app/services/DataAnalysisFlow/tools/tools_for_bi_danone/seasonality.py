import fireducks.pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import time

# Diccionario para la función get_seasonality
get_seasonality_dict = {
    "description": """Analiza la estacionalidad de los datos calculando las variaciones mes a mes del año provisto. para calcular la variación de dos o más años, se puede pasar una lista de años.
    Por ejemplo, para calcular la estacionalidad de 2023 y 2024, se puede usar: get_seasonality(df, anio=[2023, 2024]).
    Si no se especifica el año, se utilizará el año actual (2024) por defecto.
    Utiliza por defecto los filtros: TIPO_FILTRO='GPS', CATEGORIA='DAIRY', NOMBRE_ETIQUETA contiene 'REAL', MARCA existente y no 'HERSHEY's'.
    Permite filtrado adicional por año, columna personalizada y valor.
    Se utiliza cuando el usuario quiere analizar la estacionalidad o variaciones mes a mes en los datos.
    El usuario puede mencionar 'Quiero ver la estacionalidad', 'Variación mes a mes' o algo similar.
    El output de esta función es un DataFrame con las columnas 'MES_ANO', 'VALOR' y 'VARIACION' (porcentaje de cambio respecto al mes anterior) (input directo de la función crear_grafica_variacion).
    Para graficar el resultado de ambos años, se puede pasar el DataFrame a la función crear_grafica_variacion directamente, seasonalyty_df = get_seasonality(df, anio=[2023,2024]) y luego crear_grafica_variacion(seasonality_df).
    Esto dará como resultado un gráfico de variación mes a mes comparando ambos años.
    """,
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
        "description": "DataFrame con la variación mes a mes. Las columnas son 'MES_ANO', 'VALOR' y 'VARIACION' (porcentaje de cambio respecto al mes anterior)"
    }
}

def get_seasonality(df, anio=None, by_column=None, by_value=None):
    """
    Parameters:
    -----------
    df : pandas DataFrame
        Input dataframe with the raw data
    """

    # Validar que ambos parámetros by_column y by_value sean proporcionados o ninguno de los dos
    if (by_column is not None and by_value is None) or (by_column is None and by_value is not None):
        raise ValueError("Ambos parámetros by_column y by_value deben ser proporcionados o ninguno de los dos.")
    
    start = time.time()
    df_copy = df.copy()
    #print("⏱️ Tiempo con fireducks 1:", time.time() - start, "segundos")
    # df_copy["NOMBRE_ETIQUETA"] = df_copy["ETIQUETA"].str.split(" ", n=1).str[0]
    start = time.time()
    df_copy["FECHA_"] = pd.to_datetime(df_copy["FECHA"], format="%d/%m/%Y", errors='coerce')
    #
    # Añadir una columna para ordenación cronológica
    start = time.time()
    df_copy["FECHA_ORDEN"] = df_copy["FECHA_"].dt.strftime('%Y-%m')
    #print("⏱️ Tiempo con fireducks 3:", time.time() - start, "segundos")

    # Crear la columna de visualización con formato mes-año
    meses_es = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    
    start = time.time()
    #df_copy["MES_ANO"] = df_copy["FECHA_"].apply(
    #    lambda x: f"{meses_es[x.month]}-{x.year}" if pd.notnull(x) else None
    #)
    df_copy["MES_ANO"] = df_copy["FECHA_"].dt.month.map(meses_es) + '-' + df_copy["FECHA_"].dt.year.astype(str)
    #print("⏱️ Tiempo con fireducks 4:", time.time() - start, "segundos")

    filtro_base = (
        (df_copy.TIPO_FILTRO == 'GPS') & 
        (df_copy.CATEGORIA == 'DAIRY') &
        (df_copy.NOMBRE_ETIQUETA.str.contains('REAL', na=False)) &
        (df_copy.MARCA.notnull()) &
        (df_copy.MARCA != "HERSHEY's")
    )

    # Add year filter if specified
    if anio is not None:
        if isinstance(anio, list):
            filtro_base = filtro_base & (df_copy["AÑO"].isin(anio))
        else:
            filtro_base = filtro_base & (df_copy["AÑO"] == anio)
            
    # Filtro por columna y valor específicos
    if by_column is not None and by_value is not None:
        filtro_base = filtro_base & (df_copy[by_column].str.contains(by_value, na=False))

    # Aplicar todos los filtros combinados con AND
    df_filtered = df_copy[filtro_base]
    # Group by the specified column and calculate the sum of VALOR
    start = time.time()
    df_grouped = df_filtered.groupby(["MES_ANO", "FECHA_ORDEN"])['VALOR'].sum().reset_index()
    #print("⏱️ Tiempo con fireducks 5:", time.time() - start, "segundos")
    # Ordenar por la columna de ordenación (que tiene formato YYYY-MM)
    start = time.time()
    df_sorted = df_grouped.sort_values(by="FECHA_ORDEN", ascending=False)
    #print("⏱️ Tiempo con fireducks 6:", time.time() - start, "segundos")

    # Mes anterior
    start = time.time()
    df_sorted["VALOR_ANTERIOR"] = df_sorted["VALOR"].shift(-1)
    #print("⏱️ Tiempo con fireducks 7:", time.time() - start, "segundos")

    start = time.time()
    df_sorted["VARIACION"] = round(((df_sorted["VALOR"] - df_sorted["VALOR_ANTERIOR"]) / df_sorted["VALOR_ANTERIOR"]) * 100, 1)
    #print("⏱️ Tiempo con fireducks 8:", time.time() - start, "segundos")

    # Eliminar la columna de ordenación si no es necesaria en el resultado final
    start = time.time()
    df_shifted = df_sorted.drop(["FECHA_ORDEN", "VALOR_ANTERIOR"], axis=1).reset_index(drop=True)
    #print("⏱️ Tiempo con fireducks 9:", time.time() - start, "segundos")

    return df_shifted

# Diccionario para la función crear_grafica_variacion
crear_grafica_variacion_dict = {
    "description": """Crea un gráfico de variación mes a mes con área sombreada y etiquetas de valores.
    Se utiliza para visualizar gráficamente los resultados de la función get_seasonality.
    El usuario puede mencionar 'Quiero ver un gráfico de la estacionalidad', 'Visualiza la variación mes a mes' o algo similar.
    Los valores positivos aparecen en verde y los negativos en rojo.""",
    "parameters": {
        "df": {
            "type": "pd.DataFrame",
            "description": "DataFrame con la información de variación mes a mes (output de get_seasonality)",
            "required": True
        }
    },
    "returns": {
        "type": "matplotlib.figure.Figure",
        "description": "Objeto de figura de matplotlib con el gráfico de variación mes a mes"
    }
}

def crear_grafica_variacion(df):
    """
    Crea un gráfico de líneas con bullets para variaciones mensuales,
    ordenado cronológicamente de Enero a Diciembre. Detecta automáticamente
    si hay múltiples años y crea una leyenda diferenciando por color.
    
    Parameters:
    -----------
    df : pandas DataFrame
        DataFrame con columnas 'MES_ANO' y 'VARIACION'
    """
    # Hacer una copia para no modificar el original
    data = df.copy()
    
    # Extraer mes y año de la columna MES_ANO
    data['MES'] = data['MES_ANO'].str.extract(r'(\w{3})-\d{4}')
    data['AÑO'] = data['MES_ANO'].str.extract(r'\w{3}-(\d{4})')
    
    # Identificar si hay múltiples años
    años_unicos = sorted(data['AÑO'].unique())
    multiples_años = len(años_unicos) > 1
    
    # Definir el orden correcto de los meses
    orden_meses = {'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5, 'Jun': 6, 
                  'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12}
    
    # Añadir orden para ordenamiento cronológico
    data['ORDEN'] = data['MES'].map(orden_meses)
    
    # Configurar estilo de seaborn
    sns.set_style("whitegrid")
    
    # Crear figura y ejes
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
    
    # Línea horizontal en y=0
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.5, zorder=0)
    
    # Paleta de colores para múltiples años
    if multiples_años:
        palette = sns.color_palette("deep", len(años_unicos))
        color_map = {año: color for año, color in zip(años_unicos, palette)}
    else:
        color_map = {df[0]: '#1F497D'}  # Azul oscuro para un solo año
    
    # Primero, recolectar todos los valores por mes para identificar qué año viene primero
    meses_datos = {}
    for año in años_unicos:
        año_data = data[data['AÑO'] == año].copy()
        año_data = año_data.sort_values('ORDEN')
        año_data = año_data.dropna(subset=['VARIACION'])
        
        for _, row in año_data.iterrows():
            mes_num = orden_meses[row['MES']]
            if mes_num not in meses_datos:
                meses_datos[mes_num] = []
            meses_datos[mes_num].append({
                'año': año,
                'valor': row['VARIACION']
            })
    
    # Ahora, dibujar las líneas para todos los años
    for año in años_unicos:
        # Filtrar datos para este año
        año_data = data[data['AÑO'] == año].copy()
        
        # Ordenar por mes para este año
        año_data = año_data.sort_values('ORDEN').reset_index(drop=True)
        año_data = año_data.dropna(subset=['VARIACION'])  # Eliminar filas con NaN
        
        if len(año_data) == 0:
            continue
        
        # Extraer datos ordenados
        meses = año_data['MES']
        variacion = año_data['VARIACION']
        
        # Crear el eje x para los puntos (usar meses como posiciones)
        x_positions = [orden_meses[mes] for mes in meses]
        
        # Crear la línea con marcadores
        line = ax.plot(x_positions, variacion, marker='o', linewidth=2, 
                      markersize=10, color=color_map[año], zorder=3,
                      label=f'Año {año}')
    
    # Finalmente, agregar las anotaciones después de dibujar todas las líneas
    # para tener control sobre el orden de las anotaciones
    for mes_num, datos_mes in meses_datos.items():
        # Si hay múltiples años para este mes
        if len(datos_mes) > 1:
            # Ordenar por año (ascendente) para mantener el primer año como referencia
            datos_mes_ordenados = sorted(datos_mes, key=lambda x: x['año'])
            
            # El primer año siempre tiene anotación normal
            primer_dato = datos_mes_ordenados[0]
            primer_valor = primer_dato['valor']
            primer_año = primer_dato['año']
            color_primer = 'green' if primer_valor >= 0 else 'red'
            ytext_offset_primer = 12 if primer_valor >= 0 else -20
            
            ax.annotate(f"{primer_valor:.1f}%", 
                        xy=(mes_num, primer_valor), 
                        xytext=(0, ytext_offset_primer),
                        textcoords='offset points',
                        ha='center', 
                        va='bottom' if primer_valor >= 0 else 'top',
                        color=color_primer,
                        weight='bold',
                        fontsize=10,
                        zorder=4)
            
            # Para el segundo año, verificar si están cercanos
            for i in range(1, len(datos_mes_ordenados)):
                segundo_dato = datos_mes_ordenados[i]
                segundo_valor = segundo_dato['valor']
                segundo_año = segundo_dato['año']
                color_segundo = 'green' if segundo_valor >= 0 else 'red'
                
                # Determinar si están cercanos (diferencia menor a 4 puntos)
                diferencia = abs(primer_valor - segundo_valor)
                estan_cercanos = diferencia < 4.0
                
                if estan_cercanos:
                    # Si están cercanos, colocar en posición relativa al primer punto
                    if segundo_valor >= primer_valor:
                        # Si el segundo valor es mayor, colocarlo más arriba
                        ytext_offset_segundo = 35 if segundo_valor >= 0 else -5
                    else:
                        # Si el segundo valor es menor, colocarlo más abajo
                        ytext_offset_segundo = 5 if segundo_valor >= 0 else -40
                else:
                    # Si no están cercanos, usar posición normal
                    ytext_offset_segundo = 12 if segundo_valor >= 0 else -20
                
                ax.annotate(f"{segundo_valor:.1f}%", 
                            xy=(mes_num, segundo_valor), 
                            xytext=(0, ytext_offset_segundo),
                            textcoords='offset points',
                            ha='center', 
                            va='bottom' if segundo_valor >= 0 else 'top',
                            color=color_segundo,
                            weight='bold',
                            fontsize=10,
                            zorder=4)
        else:
            # Si solo hay un año para este mes, anotación normal
            dato = datos_mes[0]
            valor = dato['valor']
            año = dato['año']
            color = 'green' if valor >= 0 else 'red'
            ytext_offset = 12 if valor >= 0 else -20
            
            ax.annotate(f"{valor:.1f}%", 
                        xy=(mes_num, valor), 
                        xytext=(0, ytext_offset),
                        textcoords='offset points',
                        ha='center', 
                        va='bottom' if valor >= 0 else 'top',
                        color=color,
                        weight='bold',
                        fontsize=10,
                        zorder=4)
    
    # Mejorar la cuadrícula
    ax.grid(axis='x', linestyle='--', color='lightgray', alpha=0.7, zorder=0)
    ax.grid(axis='y', linestyle='--', color='lightgray', alpha=0.7, zorder=0)
    
    # Configurar límites y etiquetas del eje Y
    ymin, ymax = ax.get_ylim()
    buffer = (ymax - ymin) * 0.15
    ymin_with_buffer = ymin - buffer
    ymax_with_buffer = ymax + buffer
    
    # Calcular las marcas del eje Y con incrementos de 10%
    step = 10
    y_ticks = np.arange(
        step * np.floor(ymin_with_buffer / step),
        step * np.ceil(ymax_with_buffer / step) + step,
        step
    )
    
    # Establecer las etiquetas y marcas del eje Y
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{int(y)}%" for y in y_ticks], fontsize=9, color='gray')
    
    # Configurar etiquetas del eje X (nombres de los meses)
    nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                     'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    ax.set_xticks(list(range(1, 13)))
    ax.set_xticklabels(nombres_meses, rotation=0, fontsize=9)
    
    # Establecer los límites del eje X para mostrar todo el año
    ax.set_xlim(0.5, 12.5)
    
    # Establecer los límites del eje Y
    ax.set_ylim(ymin_with_buffer, ymax_with_buffer)
    
    # Añadir etiqueta al eje Y
    ax.set_ylabel('Variación (%)', fontsize=10, color='gray')
    
    # Quitar los bordes del gráfico
    sns.despine(left=True, bottom=True)
    
    # Añadir título
    if multiples_años:
        ax.set_title(f'Variación Mensual ({", ".join(años_unicos)})', fontsize=14, pad=20)
    else:
        ax.set_title(f'Variación Mensual {años_unicos[0]}', fontsize=14, pad=20)
    
    # Añadir leyenda si hay múltiples años
    if multiples_años:
        ax.legend(fontsize=9, loc='best')
    
    plt.tight_layout()
    
    return fig
