import fireducks.pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from typing import Dict, Any
import time


# Diccionario para la función get_innos_gps
get_innos_gps_dict = {
    "description": """Analiza los productos que .
    Utiliza por defecto los filtros: TIPO_FILTRO='GPS', CATEGORIA='DAIRY', NOMBRE_ETIQUETA contiene 'REAL', MARCA existente y no 'HERSHEY's', y CONCEPTO='INNO'.
    Permite filtrado adicional por año.
    Se utiliza cuando el usuario quiere identificar qué productos dentro del concepto INNO tiene considerado el GPS.
    El usuario puede mencionar 'Qué INNOs tiene considerado el GPS'.""",
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
            "default": 2024
        }
    },
    "returns": {
        "type": "pd.DataFrame",
        "description": "DataFrame con los productos más vendidos dentro del concepto INNO. Las columnas son 'AÑO', 'MARCA', 'ACTIVIDAD', 'DESCRIPCION', 'VALOR'"
    }
}

def get_innos_gps(df, anio=2024):
    """
    Parameters:
    -----------
    df : pandas DataFrame
        Input dataframe with the raw data
    anio : int, list or None, default=2024
        Year or list of years to filter by
    """
    
    df_copy = df.copy()
    # df_copy["NOMBRE_ETIQUETA"] = df_copy["ETIQUETA"].str.split(" ", n=1).str[0]
    df_copy["FECHA_"] = pd.to_datetime(df_copy["FECHA"], format="%d/%m/%Y", errors='coerce')
    
    # Añadir una columna para ordenación cronológica
    df_copy["FECHA_ORDEN"] = df_copy["FECHA_"].dt.strftime('%Y-%m')
    
    # Crear la columna de visualización con formato mes-año
    meses_es = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    
    # df_copy["MES_ANO"] = df_copy["FECHA_"].apply(
    #     lambda x: f"{meses_es[x.month]}-{x.year}" if pd.notnull(x) else None
    # )
    df_copy["MES_ANO"] = df_copy["FECHA_"].dt.month.map(meses_es) + '-' + df_copy["FECHA_"].dt.year.astype(str)

    # Construir el filtro base
    filtros = [
        (df_copy.TIPO_FILTRO == 'GPS') & 
        (df_copy.CATEGORIA == 'DAIRY') &
        (df_copy.NOMBRE_ETIQUETA.str.contains('REAL', na=False)) &
        (df_copy.MARCA.notnull()) &
        (df_copy.MARCA != "HERSHEY's") &
        (df_copy.CONCEPTO == 'INNO')
    ]

    # Filtro para año(s)
    if anio is not None:
        if isinstance(anio, list):
            # Si es una lista de años, usar operador isin
            filtros.append(df_copy["AÑO"].isin(anio))
        else:
            # Si es un solo año, usar igualdad
            filtros.append(df_copy["AÑO"] == anio)

    # Aplicar todos los filtros combinados con AND
    df_filtered = df_copy[pd.Series(True, index=df_copy.index)]
    for filtro in filtros:
        df_filtered = df_filtered[filtro]

    # Group by the specified column and calculate the sum of VALOR
    df_grouped = df_filtered.groupby(["AÑO", "MARCA", "ACTIVIDAD", "DESCRIPCION"])['VALOR'].sum().reset_index()

    # Ordenar por la columna de ordenación (que tiene formato YYYY-MM)
    df_sorted = df_grouped.sort_values(by=["VALOR"], ascending=[False])

    return df_sorted

# Diccionario para la función crear_grafica_top10_innos
crear_grafica_top10_innos_gps_dict = {
    "description": """Crea un gráfico de barras horizontales con los valores de top 10 de productos más vendidos dentro del concepto INNO.
    Se utiliza para visualizar gráficamente los resultados de la función get_innos_gps.
    El usuario puede mencionar 'Quiero ver un gráfico del top 10 de productos más vendidos dentro del concepto INNO', 'Visualiza el top 10 de productos más vendidos dentro del concepto INNO'.""",
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

def crear_grafica_top10_innos_gps(df):
    """
    Crea una gráfica de barras horizontales con los datos proporcionados.
    
    Parameters:
    -----------
    df : pandas DataFrame
        DataFrame con los datos a graficar
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Objeto figura de matplotlib
    """
    plt.ioff()
    # Configurar el estilo
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Ordenar y seleccionar los datos
    df_sorted = df.head(10).sort_values(by='VALOR', ascending=True)
    
    # Crear un diccionario de colores por marca
    marcas = df_sorted['MARCA'].unique()
    colores = [
                # Azules originales y derivados
                "#324BAA", "#11ACED", "#89C8F2", "#5BB5E9", "#4CABE4",
                "#1E3F8A", "#A3D9F9", "#E6F5FD",

                # Fucsias / Rosas intensos
                "#F72585", "#FF4FA0", "#FF9EC9", "#D61C88",

                # Verdes tipo aqua / menta
                "#2ED9C3", "#54E1C2", "#B3F4EB", "#0FC2C0",

                # Rojos
                "#F44336", "#E53935", "#FF6B6B", "#B71C1C"
            ]
    color_dict = dict(zip(marcas, colores))
    
    # Lista para almacenar los colores de cada barra
    bar_colors = [color_dict[marca] for marca in df_sorted['MARCA']]
    
    # Crear barras horizontales usando matplotlib directamente
    bars = ax.barh(
        y=range(len(df_sorted)),
        width=df_sorted['VALOR'],
        color=bar_colors,
        height=0.7,
        align='center',
        linewidth=0  # Eliminar líneas de las barras
    )
    
    # Configurar las etiquetas del eje Y (descripciones de productos)
    ax.set_yticks(range(len(df_sorted)))
    ax.set_yticklabels(df_sorted['DESCRIPCION'])
    
    # Añadir valores al final de las barras
    for i, valor in enumerate(df_sorted['VALOR']):
        ax.text(
            valor + 5,          # Posición X (ligeramente a la derecha)
            i,                  # Posición Y (índice de la barra)
            f"{valor:.2f}",     # Formato del valor con 2 decimales
            va='center',        # Alineación vertical centrada
            ha='left',          # Alineación horizontal a la izquierda
            fontweight='bold',  # Negrita
            fontsize=9          # Tamaño de fuente
        )
    
    # Crear leyenda para las marcas
    legend_elements = [Patch(facecolor=color_dict[marca], label=marca, linewidth=0) 
                      for marca in color_dict]
    ax.legend(handles=legend_elements, title='MARCA', loc='lower right')
    
    # Configurar el título y etiquetas de ejes
    ax.set_title('Top Productos por Valor de Venta', fontsize=16, pad=20)
    ax.set_xlabel('VALOR', fontsize=12)
    ax.set_ylabel('PRODUCTO', fontsize=12)
    
    # Eliminar los bordes del gráfico
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_alpha(0.3)
    ax.spines['bottom'].set_alpha(0.3)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    fig.tight_layout()

    return fig

