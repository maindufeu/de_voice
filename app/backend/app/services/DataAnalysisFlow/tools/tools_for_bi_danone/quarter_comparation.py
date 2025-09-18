import fireducks.pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from typing import Dict, Any
import time


# Diccionario para la función get_pivoted_df
get_pivoted_df_dict = {
    "description": """Obtiene un DataFrame pivotado con valores trimestrales para cada año y tipo (REAL/GPS). **Este pivoted_df ya incluye los datos reales y los de GPS de todos los años disponibles en el dataset.**
    Utiliza por defecto los filtros: CATEGORIA='DAIRY'. Este filtro sólo se cambia si el objetivo lo exige explícitamente.
    Se utiliza cuando el usuario quiere comparar valores trimestrales globales, se da como input el dataframe de ventas, 
    y devuelve un dataframe pivotado con los valores trimestrales que incluyen cada año de ventas reales y cada año de predicciones 
    de los años disponibles del dataset.
    El producto de esta función se usa en las funciones 'compare_real_years' y 'compare_real_vs_predicted'.
    El usuario puede mencionar 'Quiero ver los valores trimestrales de este año', 'Cuánto crece cada q vs q' o algo similar.""",
    "parameters": {
        "df": {
            "type": "pd.DataFrame",
            "description": "DataFrame de entrada con los datos en bruto",
            "required": True
        },
        "category": {
            "type": "str",
            "description": "Categoría para filtrar los datos",
            "required": False,
            "default": "DAIRY"
        }
    },
    "returns": {
        "type": "pd.DataFrame",
        "description": "DataFrame pivotado con valores trimestrales (columnas ['Q1', 'Q2', 'Q3', 'Q4']) para cada etiqueta (filas ['REAL <AÑO-1>', 'REAL <AÑO>', 'GPS <AÑO-1>', 'GPS <AÑO>'])"
    }
}

def get_pivoted_df(df, category='DAIRY'):
    """
    Obtiene un DataFrame pivotado con valores trimestrales para cada año y tipo (REAL/GPS)
    
    Parámetros:
    -----------
    df : pandas DataFrame
        DataFrame de entrada con los datos en bruto
    category : str, default='DAIRY'
        Categoría para filtrar los datos
        
    Retorna:
    --------
    pandas DataFrame
        DataFrame pivotado con valores trimestrales
    """
    # 1. Crear un mapeo para Q y MES
    q_relation = pd.DataFrame({
        'Q': ['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q3', 'Q3', 'Q3', 'Q4', 'Q4', 'Q4'],
        'MES': ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
    })

    # 2. Obtener un DataFrame filtrado con solo las columnas relevantes
    df_filtered = df[['AÑO', 'MES', 'ETIQUETA', 'VALOR']][
        (df.CATEGORIA == category) & (df.TIPO_FILTRO == 'GPS')
    ]

    # 3. Combinar con la relación Q para obtener la columna Q
    df_filtered = df_filtered.merge(q_relation, on='MES', how='left')

    # 4. Calcular los valores reales y predichos para cada Q
    df_pivoted = df_filtered.groupby(['ETIQUETA','Q']).agg({'VALOR': 'sum'}).reset_index()
    df_pivoted = df_pivoted.pivot(index='ETIQUETA', columns='Q', values='VALOR')
    df_pivoted.columns.name = None  # Eliminar el nombre de las columnas
    
    return df_pivoted

# Diccionario para la función compare_real_years
compare_real_years_dict = {
    "description": """Compara los valores reales trimestrales entre el año actual y el año anterior.
    Utiliza por defecto los años actuales (el definido como current_year (2024) y previous_year 2023).
    Estos años sólo se cambian si el objetivo lo exige explícitamente. 
    Si se desea comparar años distintos, se debe especificar el año actual y el año anterior mediante ```compare_real_years(df_pivoted, current_year=2024, year_to_compare=2023)```.
    Se utiliza cuando el usuario quiere comparar los valores reales de un año con los del año anterior.
    El usuario puede mencionar 'Quiero ver el crecimiento por q de este año frente al año pasado', 
    'Cuánto crece cada q vs q' o algo similar.
    Sugerencia para graficar los resultados: usar la función crear_grafica_comparacion.""",
    "parameters": {
        "df_pivoted": {
            "type": "pd.DataFrame",
            "description": "DataFrame pivotado con valores trimestrales (output de get_pivoted_df)",
            "required": True
        },
        "current_year": {
            "type": "int",
            "description": "Año actual para la comparación. Por defecto usa 2024",
            "required": False,
            "default": 2024
        },
        "year_to_compare": {
            "type": "int",
            "description": "Año anterior para la comparación. Por defecto usa 2023",
            "required": False,
            "default": 2023
        }
    },
    "returns": {
        "type": "pd.DataFrame",
        "description": "DataFrame con valores reales de ambos años y porcentaje de crecimiento por trimestre. Las columnas son 'REAL <AÑO>', 'REAL <AÑO_ACTUAL>' y 'GROWTH %', mientras que las filas son los trimestres (Q1, Q2, Q3, Q4)"
    }
}

def compare_real_years(df_pivoted, current_year=2024, year_to_compare=2023):
    """
    Compara los valores reales trimestrales entre el año actual y el año anterior
    
    Parámetros:
    -----------
    df_pivoted : pandas DataFrame
        DataFrame pivotado con valores trimestrales
    current_year : int, default=2024
        Año actual para la comparación
    year_to_compare : int, default=2023
        Año anterior para la comparación
        
    Retorna:
    --------
    pandas DataFrame
        DataFrame con valores reales de ambos años y porcentaje de crecimiento
    """
    growth = {
        'Q1': ((df_pivoted.loc[f"REAL {current_year}"]['Q1'] - df_pivoted.loc[f"REAL {year_to_compare}"]['Q1']) / df_pivoted.loc[f"REAL {year_to_compare}"]['Q1']) * 100,
        'Q2': ((df_pivoted.loc[f"REAL {current_year}"]['Q2'] - df_pivoted.loc[f"REAL {year_to_compare}"]['Q2']) / df_pivoted.loc[f"REAL {year_to_compare}"]['Q2']) * 100,
        'Q3': ((df_pivoted.loc[f"REAL {current_year}"]['Q3'] - df_pivoted.loc[f"REAL {year_to_compare}"]['Q3']) / df_pivoted.loc[f"REAL {year_to_compare}"]['Q3']) * 100,
        'Q4': ((df_pivoted.loc[f"REAL {current_year}"]['Q4'] - df_pivoted.loc[f"REAL {year_to_compare}"]['Q4']) / df_pivoted.loc[f"REAL {year_to_compare}"]['Q4']) * 100
    }

    return pd.DataFrame({
        f'REAL {year_to_compare}': df_pivoted.loc[f"REAL {year_to_compare}"],
        f'REAL {current_year}': df_pivoted.loc[f"REAL {current_year}"],
        'GROWTH %': growth
    })

# Diccionario para la función compare_real_vs_predicted
compare_real_vs_predicted_dict = {
    "description": """Compara los valores reales frente a los valores GPS pronosticados para un año específico.
    Se utiliza cuando el usuario quiere comparar por trimestre la venta real vs la pronosticada.
    El usuario puede mencionar 'Quiero comparar los valores reales de este año con los pronosticados por q', 
    'Las ventas por q reales vs las pronosticadas' o algo similar.
    Sugerencia para graficar los resultados: usar la función crear_grafica_comparacion.""",
    "parameters": {
        "df_pivoted": {
            "type": "pd.DataFrame",
            "description": "DataFrame pivotado con valores trimestrales",
            "required": True
        },
        "year": {
            "type": "int",
            "description": "Año para realizar la comparación",
            "required": False,
            "default": 2024
        }
    },
    "returns": {
        "type": "pd.DataFrame",
        "description": "DataFrame con valores reales, valores pronosticados y porcentaje de diferencia por trimestre. Las columnas son 'REAL <AÑO>', 'PREDICTED <AÑO>' y 'DIFFERENCE %', mientras que las filas son los trimestres (Q1, Q2, Q3, Q4)"
    }
}

def compare_real_vs_predicted(df_pivoted, year=2024):
    """
    Compara los valores reales frente a los valores GPS pronosticados para un año específico
    
    Parámetros:
    -----------
    df_pivoted : pandas DataFrame
        DataFrame pivotado con valores trimestrales
    year : int, default=2024
        Año para realizar la comparación
        
    Retorna:
    --------
    pandas DataFrame
        DataFrame con valores reales, valores pronosticados y porcentaje de diferencia
    """
    difference = {
        'Q1': ((df_pivoted.loc[f"REAL {year}"]['Q1'] - df_pivoted.loc[f"GPS {year}"]['Q1']) / df_pivoted.loc[f"GPS {year}"]['Q1']) * 100,
        'Q2': ((df_pivoted.loc[f"REAL {year}"]['Q2'] - df_pivoted.loc[f"GPS {year}"]['Q2']) / df_pivoted.loc[f"GPS {year}"]['Q2']) * 100,
        'Q3': ((df_pivoted.loc[f"REAL {year}"]['Q3'] - df_pivoted.loc[f"GPS {year}"]['Q3']) / df_pivoted.loc[f"GPS {year}"]['Q3']) * 100,
        'Q4': ((df_pivoted.loc[f"REAL {year}"]['Q4'] - df_pivoted.loc[f"GPS {year}"]['Q4']) / df_pivoted.loc[f"GPS {year}"]['Q4']) * 100
    }

    return pd.DataFrame({
        f'REAL {year}': df_pivoted.loc[f"REAL {year}"],
        f'PREDICTED {year}': df_pivoted.loc[f"GPS {year}"],
        'DIFFERENCE %': difference
    })



# Diccionario para la función crear_grafica_comparacion
crear_grafica_comparacion_dict = {
    "description": """Crea un gráfico de barras que muestra las diferencias o crecimiento por trimestre (q).
    Se utiliza para visualizar gráficamente los resultados de las funciones compare_real_vs_predicted y compare_real_years.
    El usuario puede mencionar 'Quiero ver un gráfico de las diferencias por trimestre', 'Muestra el crecimiento por trimestre', 
    'compara q vs q...', 'compara los q`s', o algo similar.
    Para usarla, se pasa directamente el output de las funciones compare_real_vs_predicted o compare_real_years; por ejemplo ```comparative_df = compare_real_years(pivoted_df); crear_grafica_comparacion(comparative_df)```.
    Las barras son verdes para valores positivos y rojas para valores negativos.""",
    "parameters": {
        "df": {
            "type": "pd.DataFrame",
            "description": "DataFrame con las diferencias por trimestre (output de compare_real_vs_predicted o compare_real_years)",
            "required": True
        }
    },
    "returns": {
        "type": "matplotlib.figure.Figure",
        "description": "Objeto de figura de matplotlib con el gráfico de barras por trimestre"
    }
}

def crear_grafica_comparacion(df):
    """
    Crea un gráfico de barras que muestra las diferencias o crecimiento por trimestre
    
    Parámetros:
    -----------
    df : pandas DataFrame
        DataFrame con las diferencias por trimestre
        
    Retorna:
    --------
    matplotlib.figure.Figure
        Objeto figura de matplotlib
    """
    # Determinar qué tipo de comparación es basado en las columnas
    is_growth = 'GROWTH %' in df.columns
    diff_column = 'GROWTH %' if is_growth else 'DIFFERENCE %'
    
    # Extraer años de los nombres de las columnas
    years = []
    for col in df.columns:
        if col not in [diff_column, 'GROWTH %', 'DIFFERENCE %']:
            if 'REAL' in col:
                year = col.replace('REAL ', '')
                years.append(year)
            elif 'PREDICTED' in col:
                year = col.replace('PREDICTED ', '')
                if year not in years:
                    years.append(year)
    
    years_str = "(" + " vs ".join(years)+")" if years else ""
    
    # Configurar el estilo
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    
    # Crear las barras
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    values = df[diff_column]
    colors = ['green' if x >= 0 else 'red' for x in values]
    
    bars = plt.bar(quarters, values, color=colors)
    
    # Añadir valores en las barras
    for bar in bars:
        height = bar.get_height()
        y_pos = height + 1 if height >= 0 else height - 2
        plt.text(bar.get_x() + bar.get_width()/2., y_pos,
                f'{height:.1f}%',
                ha='center', va='bottom' if height >= 0 else 'top',
                fontweight='bold', fontsize=11)
    
    # Configurar el gráfico
    ylabel = 'Crecimiento (%)' if is_growth else 'Diferencia (%)'
    title_prefix = 'Crecimiento por Trimestre' if is_growth else 'Diferencia por Trimestre'
    title = f'{title_prefix} {years_str}'.strip()
    
    plt.title(title, pad=20, fontsize=14)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, axis='y', alpha=0.3)
    
    # Ajustar los límites del eje y para dar espacio a las etiquetas
    y_min, y_max = plt.ylim()
    plt.ylim(y_min - 5, y_max + 5)
    
    # Quitar bordes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return plt.gcf()

