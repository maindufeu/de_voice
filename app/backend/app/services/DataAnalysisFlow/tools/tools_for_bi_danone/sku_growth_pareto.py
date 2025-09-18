import fireducks.pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from typing import Dict, Any
import time


# Diccionario para la función analyze_sku_pareto
analyze_sku_pareto_dict = {
    "description": """Analiza los SKUs utilizando el principio de Pareto (regla 80/20). 
    Utiliza por defecto los filtros: CATEGORIA='DAIRY', TIPO_FILTRO='GPS', CONCEPTO='INNO' y VALOR>0.
    Estos filtros sólo se cambian si se especifican otros valores en los parámetros.
    Se utiliza cuando el usuario quiere ver qué SKUs representan el 20% del valor total.
    El usuario puede mencionar 'Cuáles son los SKUs que representan el 20% del valor total', 'Cuáles son los SKUs que más aportan al total', '¿Cuáles son los SKUs que representan el 20% de las ventas?' o algo similar.
    Si se utiliza esta función para una gráfica, se debe mostrar la descripción, no el sku en el detalle de la gráfica.
    """,
    "parameters": {
        "df": {
            "type": "pd.DataFrame",
            "description": "DataFrame de entrada con los datos en bruto",
            "required": True
        },
        "categoria": {
            "type": "str",
            "description": "Categoría para filtrar los datos",
            "required": False,
            "default": "DAIRY"
        },
        "tipo_filtro": {
            "type": "str",
            "description": "Tipo de filtro a utilizar",
            "required": False,
            "default": "GPS"
        },
        "etiqueta_contains": {
            "type": "str",
            "description": "Texto que debe contener la etiqueta",
            "required": False,
            "default": "REAL"
        },
        "concepto_exclude": {
            "type": "str",
            "description": "Concepto a excluir del análisis",
            "required": False,
            "default": "INNO"
        },
        "valor_min": {
            "type": "float",
            "description": "Valor mínimo a considerar",
            "required": False,
            "default": 0
        },
        "min_years": {
            "type": "int",
            "description": "Número mínimo de años en los que debe aparecer el SKU",
            "required": False,
            "default": 2
        },
        "anio": {
            "type": "int",
            "description": "Año(s) para realizar el análisis",
            "required": False,
            "default": 2024
        }
    },
    "returns": {
        "type": "pd.DataFrame",
        "description": "DataFrame con los SKUs que conforman el 80% del valor total. Los nombres de las columnas son 'VALOR_TOTAL', 'PORCENTAJE', 'PORCENTAJE_ACUMULADO' y 'DESCRIPCION'"    }
}

def analyze_sku_pareto(df, categoria='DAIRY', tipo_filtro='GPS', etiqueta_contains='REAL', 
                      concepto_exclude='INNO', valor_min=0, min_years=None, anio=None):
    """
    Analiza los SKUs utilizando el principio de Pareto (regla 80/20)
    
    Parámetros:
    -----------
    df : pandas DataFrame
        DataFrame de entrada con los datos en bruto
    categoria : str, default='DAIRY'
        Categoría para filtrar los datos
    tipo_filtro : str, default='GPS'
        Tipo de filtro a utilizar
    etiqueta_contains : str, default='REAL'
        Texto que debe contener la etiqueta
    concepto_exclude : str, default='INNO'
        Concepto a excluir del análisis
    valor_min : float, default=0
        Valor mínimo a considerar
    min_years : int, default=None
        Número mínimo de años en los que debe aparecer el SKU
    anio : int o list, default=None
        Año o lista de años específicos para filtrar
        
    Retorna:
    --------
    pandas DataFrame
        DataFrame con los SKUs que conforman el 80% del valor total
    """
    # 1. Filtrar datos - Corregido el método de filtrado
    filtros = [
        df.ETIQUETA.str.contains(etiqueta_contains),
        df.CONCEPTO != concepto_exclude,
        df.VALOR > valor_min,
        df.CATEGORIA == categoria,
        df.TIPO_FILTRO == tipo_filtro
    ]
    
    # Filtro para año(s)
    if anio is not None:
        if isinstance(anio, list):
            # Si es una lista de años, usar operador isin
            filtros.append(df.AÑO.isin(anio))
        else:
            # Si es un solo año, usar igualdad
            filtros.append(df.AÑO == anio)
    
    # Aplicar todos los filtros
    df_skus_validos = df[np.logical_and.reduce(filtros)]
    
    # 2. Obtener SKUs presentes en el número mínimo de años especificado
    if min_years is not None:
        skus_by_year = df_skus_validos.groupby('SKU')['AÑO'].nunique()
        valid_skus = skus_by_year[skus_by_year >= min_years].index
        df_comparable = df_skus_validos[df_skus_validos.SKU.isin(valid_skus)]
    else:
        df_comparable = df_skus_validos
    
    # 3. Calcular valor total por SKU
    total_valor_by_sku = df_comparable.groupby('SKU')['VALOR'].sum().sort_values(ascending=False)
    
    # 4. Calcular porcentaje acumulado
    total_valor = total_valor_by_sku.sum()
    cumulative_percentage = (total_valor_by_sku.cumsum() / total_valor) * 100
    
    # 5. Filtrar SKUs que conforman el 80%
    skus_80_percent = cumulative_percentage[cumulative_percentage <= 80].index
    
    # 6. Crear DataFrame final
    sku_descriptions = df_comparable[['SKU', 'DESCRIPCION']].drop_duplicates().set_index('SKU')
    result = pd.DataFrame({
        'VALOR_TOTAL': total_valor_by_sku,
        'PORCENTAJE': (total_valor_by_sku / total_valor) * 100,
        'PORCENTAJE_ACUMULADO': cumulative_percentage
    })
    
    # Añadir descripciones
    result = result.join(sku_descriptions)
    result = result.sort_values(by="PORCENTAJE_ACUMULADO", ascending=True)
    
    return result.round(2)

# Diccionario para la función crear_grafica_pareto
crear_grafica_pareto_dict = {
    "description": """Crea un gráfico de barras horizontales con los valores del pareto.
    Se utiliza para visualizar gráficamente los resultados de la función analyze_sku_pareto.
    El usuario puede mencionar 'Quiero ver un gráfico de Pareto', 'CUáles son los sku que hacen el 20% de las ventas?'.""",
    "parameters": {
        "df": {
            "type": "pd.DataFrame",
            "description": "DataFrame con la información de variación mes a mes (output de analyze_sku_pareto)",
            "required": True
        },
        "porcentaje_limite": {
            "type": "float",
            "description": "Porcentaje acumulado límite hasta el cual mostrar los datos (de 0 a 100)",
            "required": False,
            "default": 20
        }
    },
    "returns": {
        "type": "matplotlib.figure.Figure",
        "description": "Objeto de figura de matplotlib con el gráfico de variación mes a mes"
    }
}

def crear_grafica_pareto(df, porcentaje_limite=20):
    """
    Crea una gráfica de barras horizontales simple con los datos proporcionados,
    mostrando solo los productos con mayor participación hasta un límite acumulado.
   
    Parameters:
    -----------
    df : pandas DataFrame
        DataFrame con los datos a graficar. Debe contener las columnas:
        - DESCRIPCION: Nombre del producto/categoría
        - PORCENTAJE: Porcentaje individual de cada elemento 
    porcentaje_limite : float, default=20
        Porcentaje acumulado límite hasta el cual mostrar los datos (de 0 a 100)
       
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Objeto figura de matplotlib
    """
    plt.ioff()
    # Configurar el estilo
    sns.set_style("whitegrid")
    
    # Ordenar los datos por porcentaje individual (de mayor a menor)
    df_sorted = df.sort_values(by='PORCENTAJE', ascending=True).reset_index(drop=True)
    
    # Calcular el porcentaje acumulado para filtrado
    total = df_sorted['PORCENTAJE'].sum()
    acumulado = 0
    porcentaje_acumulado = []
    
    for porcentaje in df_sorted['PORCENTAJE']:
        acumulado += porcentaje
        acum_percent = (acumulado / total * 100)
        porcentaje_acumulado.append(acum_percent)
    
    df_sorted['PORCENTAJE_ACUMULADO'] = porcentaje_acumulado
    
    # Filtrar solo hasta el porcentaje límite
    df_filtrado = df_sorted[(100 - df_sorted['PORCENTAJE_ACUMULADO']) <= porcentaje_limite]
    
    # Calcular el tamaño de la figura basado en el número de elementos
    num_elementos = len(df_filtrado)
    
    if num_elementos == 0:
        # Si no hay datos, usar un tamaño estándar
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, f"No hay productos que individualmente sumen menos del {porcentaje_limite}%", 
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        return fig
    
    # Calcular el alto proporcional al número de elementos (más elementos = figura más alta)
    # Base de 5 para el alto, más 0.5 por cada elemento
    height = max(5, 2 + num_elementos * 0.5)
    
    # Calcular el ancho basado en la longitud máxima de las descripciones
    max_desc_length = max(len(str(desc)) for desc in df_filtrado['DESCRIPCION'])
    # Base de 8 para el ancho, más 0.05 por cada carácter en la descripción más larga
    width = max(8, 8 + max_desc_length * 0.05)
    
    # Crear figura con tamaño adaptado
    fig, ax = plt.subplots(figsize=(width, height))

    # Ajustar los límites del eje Y para que se vea bien
    ax.set_ylim(-0.5, len(df_filtrado)-0.5) 
    
    # Color para las barras
    color_barras = '#5BB5E9FF'
    
    # Posiciones para las barras
    posiciones = np.arange(len(df_filtrado))
    
    # Crear barras para los porcentajes individuales
    bars = ax.barh(
        y=posiciones,
        width=df_filtrado['PORCENTAJE'],
        color=color_barras,
        height=0.7,
        align='center',
        linewidth=0
    )
    
    # Configurar las etiquetas del eje Y (descripciones de productos)
    ax.set_yticks(posiciones)
    ax.set_yticklabels(df_filtrado['DESCRIPCION'])
    
    # Ajustar límites del eje X basado en el valor máximo
    max_valor = df_filtrado['PORCENTAJE'].max()
    ax.set_xlim(0, max_valor * 1.15)  # 15% adicional para texto
    
    # Añadir valores al final de las barras
    for i, valor in enumerate(df_filtrado['PORCENTAJE']):
        ax.text(
            valor + max_valor * 0.01,  # Posición X basada en valor máximo
            i,                         # Posición Y (índice de la barra)
            f"{valor:.2f}%",           # Formato del valor con 2 decimales
            va='center',               # Alineación vertical centrada
            ha='left',                 # Alineación horizontal a la izquierda
            fontweight='bold',         # Negrita
            fontsize=9                 # Tamaño de fuente
        )
    
    # Configurar títulos y etiquetas
    ax.set_title(f'{len(df_filtrado)} Productos con mayor participación', fontsize=16, pad=5)
    ax.set_xlabel('PORCENTAJE INDIVIDUAL (%)', fontsize=12)
    
    # Eliminar los bordes del gráfico
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_alpha(0.3)
    ax.spines['bottom'].set_alpha(0.3)
    
    # Poner la cuadrícula detrás de las barras
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Ajustar los márgenes automáticamente
    plt.tight_layout()
    
    return fig

# Diccionario para la función analyze_sku_growth
analyze_sku_growth_dict = {
    "description": """Analiza el crecimiento de los SKUs entre años.
    Utiliza por defecto los filtros: CATEGORIA='DAIRY', TIPO_FILTRO='GPS', CONCEPTO='INNO' y VALOR>0.
    Estos filtros sólo se cambian si se especifican otros valores en los parámetros.
    Se utiliza cuando el usuario quiere ver el crecimiento de los SKUs entre dos años.
    Los parámetros current_year y year_to_compare se utilizan para especificar los años a comparar.
    El usuario puede mencionar 'Cuáles son los top 10 SKUs por crecimiento', 'Cuáles son los SKUs que más crecieron' o algo similar.
    Si se utiliza esta función para una gráfica, se debe mostrar la descripción, no el sku en el detalle de la gráfica.""",    
    "parameters": {
        "df": {
            "type": "pd.DataFrame",
            "description": "DataFrame de entrada con los datos en bruto",
            "required": True
        },
        "top_skus": {
            "type": "int",
            "description": "Número de SKUs a mostrar",
            "required": False,
            "default": 10
        },
        "etiqueta_contains": {
            "type": "str",
            "description": "Texto que debe contener la etiqueta",
            "required": False,
            "default": "REAL"
        },
        "concepto_exclude": {
            "type": "str",
            "description": "Concepto a excluir del análisis",
            "required": False,
            "default": "INNO"
        },
        "valor_min": {
            "type": "float",
            "description": "Valor mínimo a considerar",
            "required": False,
            "default": 0
        },
        "categoria": {
            "type": "str",
            "description": "Categoría para filtrar los datos",
            "required": False,
            "default": "DAIRY"
        },
        "tipo_filtro": {
            "type": "str",
            "description": "Tipo de filtro a utilizar",
            "required": False,
            "default": "GPS"
        },
        "current_year": {
            "type": "int",
            "description": "Año actual para la comparación",
            "required": False,
            "default": 2024
        },
        "year_to_compare": {
            "type": "int",
            "description": "Año anterior para la comparación",
            "required": False,
            "default": 2023
        }
    },
    "returns": {
        "type": "pd.DataFrame",
        "description": """DataFrame con los 10 principales SKUs por crecimiento. 
        Las columnas son 'DESCRIPCION', 'total_value', '<year_to_compare>', '<current_year>' y 'growth'"""
    }
}

def analyze_sku_growth(df, top_skus=10, etiqueta_contains='REAL', concepto_exclude='INNO', 
                      valor_min=0, categoria='DAIRY', tipo_filtro='GPS', 
                      current_year=2024, year_to_compare=2023):
    """
    Analiza el crecimiento de SKUs entre años
    
    Parámetros:
    -----------
    df : pandas DataFrame
        DataFrame de entrada con los datos en bruto
    top_skus : int
        Número de SKUs a mostrar
    etiqueta_contains : str, default='REAL'
        Texto que debe contener la etiqueta
    concepto_exclude : str, default='INNO'
        Concepto a excluir del análisis
    valor_min : float, default=0
        Valor mínimo a considerar
    categoria : str, default='DAIRY'
        Categoría para filtrar los datos
    tipo_filtro : str, default='GPS'
        Tipo de filtro a utilizar
    current_year : int, default=2024
        Año actual para la comparación
    year_to_compare : int, default=2023
        Año anterior para la comparación
        
    Retorna:
    --------
    pandas DataFrame
        DataFrame con los 10 principales SKUs por crecimiento
    """
    # 1. Filtrar datos
    df_skus_validos = df[
        df.ETIQUETA.str.contains(etiqueta_contains) & 
        #(df.CONCEPTO != concepto_exclude) & 
        (df.VALOR > valor_min) &
        (df.CATEGORIA == categoria) &
        (df.TIPO_FILTRO == tipo_filtro) &
        (df.AÑO.isin([current_year, year_to_compare]))
    ]

    # 2. Obtener SKUs presentes en ambos años
    # skus_current = set(df_skus_validos[df_skus_validos.AÑO == current_year]['SKU'].unique())
    # skus_compare = set(df_skus_validos[df_skus_validos.AÑO == year_to_compare]['SKU'].unique())
    # valid_skus = list(skus_current.intersection(skus_compare))

    # Create pivot table to check data presence
    valor_by_sku = df_skus_validos.groupby('SKU')['VALOR'].sum()

    # Get SKUs with total value above threshold
    valid_skus = valor_by_sku[valor_by_sku > 1655].index.tolist()
    
    df_comparable = df_skus_validos[df_skus_validos.SKU.isin(valid_skus)]

    # 3. Agrupar por SKU y año, sumar valores
    valor_by_sku_year = df_comparable.groupby(['SKU', 'AÑO'])['VALOR'].sum().reset_index()

    # 4. Pivotar los datos para tener años como columnas
    valor_pivot = valor_by_sku_year.pivot(index='SKU', columns='AÑO', values='VALOR')

    # 5. Calcular porcentaje de crecimiento
    valor_pivot['growth'] = ((valor_pivot[current_year] - valor_pivot[year_to_compare]) / valor_pivot[year_to_compare]) * 100

    # 6. Ordenar por crecimiento y obtener los 10 principales SKUs
    top_growth = valor_pivot.sort_values('growth', ascending=False).head(top_skus)

    # 7. Añadir descripciones de SKU
    sku_descriptions = df_comparable[['SKU', 'DESCRIPCION']].drop_duplicates().set_index('SKU')
    top_growth = top_growth.join(sku_descriptions)

    # 8. Calcular valor total y reordenar columnas
    top_growth['total_value'] = top_growth[year_to_compare] + top_growth[current_year]
    
    # Convertir los años (columnas) a string para evitar problemas de serialización con int64
    top_growth = top_growth.rename(columns={
        year_to_compare: str(year_to_compare),
        current_year: str(current_year)
    })
    
    top_growth = top_growth[['DESCRIPCION', 'total_value', str(year_to_compare), str(current_year), 'growth']]

    print(f"\nTop {top_skus} SKUs por crecimiento con valores totales:")
    return top_growth.round(2)

