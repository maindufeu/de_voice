import fireducks.pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from typing import Dict, Any
import time



# Diccionario para la función create_grupo_marca_matrix
create_grupo_marca_matrix_dict = {
    "description": """Crea una matriz que compara valores GPS vs Real agrupados por GRUPO y MARCA. (MAPE, mape)
    Utiliza por defecto los filtros: CATEGORIA='DAIRY', TIPO_FILTRO='GPS', CONCEPTO='INNO' y VALOR>0.
    Estos filtros sólo se cambian si se especifican otros valores en los parámetros.
    Se utiliza cuando el usuario quiere comparar los valores GPS y reales de un grupo específico de productos (GRUPO y MARCA).
    El usuario puede mencionar 'Quiero ver el error del GPS' o 'Quiero ver la diferencia entre el GPS y los valores reales', 'quiero ver el mape del gps', 'quiero ver el mape' o algo similar.""",
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
        }
    },
    "returns": {
        "type": "pd.DataFrame",
        "description": "Matriz de diferencias porcentuales entre valores GPS y reales agrupados por GRUPO y MARCA. Las filas son los grupos y las columnas son las marcas. Los valores son porcentajes."
    }
}

def create_grupo_marca_matrix(df, categoria='DAIRY', tipo_filtro='GPS', 
                            concepto_exclude='INNO', valor_min=0):
    """
    Crea una matriz que compara valores GPS vs Real agrupados por GRUPO y MARCA
    
    Parámetros:
    -----------
    df : pandas DataFrame
        DataFrame de entrada con los datos en bruto
    categoria : str, default='DAIRY'
        Categoría para filtrar los datos
    tipo_filtro : str, default='GPS'
        Tipo de filtro a utilizar
    concepto_exclude : str, default='INNO'
        Concepto a excluir del análisis
    valor_min : float, default=0
        Valor mínimo a considerar
        
    Retorna:
    --------
    pandas DataFrame
        Matriz con GRUPO como filas y MARCA como columnas
    """
    # Filtrar datos
    df_filtered = df[
        (df.CONCEPTO != concepto_exclude) & 
        (df.VALOR > valor_min) &
        (df.CATEGORIA == categoria) &
        (df.TIPO_FILTRO == tipo_filtro)
    ]
    
    # Dividir en DataFrames GPS y REAL
    df_gps = df_filtered[df_filtered.ETIQUETA.str.contains('GPS')]
    df_real = df_filtered[df_filtered.ETIQUETA.str.contains('REAL')]
    
    # Agrupar por GRUPO y MARCA
    gps_grouped = df_gps.groupby(['GRUPO', 'MARCA'])['VALOR'].sum()
    real_grouped = df_real.groupby(['GRUPO', 'MARCA'])['VALOR'].sum()
    
    # Calcular métrica de diferencia
    diff = abs(gps_grouped - real_grouped)
    result = diff / real_grouped
    
    # Pivotar para crear matriz
    matrix = result.unstack()
    matrix = matrix.round(4) * 100  # Convertir a porcentaje
    return  matrix.reset_index()

# Diccionario para la función create_heatmap_with_totals
create_heatmap_with_totals_dict = {
    "description": "Crea un mapa de calor (heatmap) con totales de filas y columnas para visualizar diferencias entre GPS y valores reales",
    "parameters": {
        "matrix": {
            "type": "pd.DataFrame",
            "description": "Matriz calculada de entrada con los valores para el mapa de calor. (Output de create_grupo_marca_matrix)",
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
        }
    },
    "returns": {
        "type": "matplotlib.figure.Figure",
        "description": "Objeto de figura de matplotlib con el mapa de calor de diferencias porcentuales entre valores reales y GPS"
    }
}

def create_heatmap_with_totals(matrix, categoria='DAIRY', tipo_filtro='GPS'):
    """
    Crea un mapa de calor (heatmap) con totales de filas y columnas para visualizar 
    diferencias entre GPS y valores reales
    
    Parámetros:
    -----------
    matrix : pandas DataFrame
        Matriz calculada de entrada con los valores para el mapa de calor
    categoria : str, default='DAIRY'
        Categoría para filtrar los datos
    tipo_filtro : str, default='GPS'
        Tipo de filtro a utilizar
        
    Retorna:
    --------
    matplotlib.figure.Figure
        Objeto de figura de matplotlib con el mapa de calor
    """
    # Hacer una copia para no modificar el original
    matrix_copy = matrix.copy()
    
    # Convertir la matriz para usar GRUPO como índice si no lo es ya
    if 'GRUPO' in matrix_copy.columns:
        matrix_copy = matrix_copy.set_index('GRUPO')
    
    # Calcular totales de filas y columnas
    row_totals = matrix_copy.mean(axis=1).round(2)
    col_totals = matrix_copy.mean(axis=0).round(2)
    
    # Añadir totales a la matriz
    matrix_copy['Total'] = row_totals
    matrix_copy.loc['Total'] = col_totals
    
    # Crear figura con mayor tamaño
    plt.figure(figsize=(15, 12))
    
    # Crear mapa de calor con tamaño de fuente mayor para anotaciones
    sns.heatmap(matrix_copy, 
                annot=True, 
                fmt='.1f',
                cmap='RdYlBu',
                center=0,
                vmin=-50,
                vmax=50,
                annot_kws={"size": 12},
                cbar_kws={'label': 'Diferencia %'})
    
    # Añadir título con detalles de la categoría y tipo de filtro
    plt.title(f'Diferencia porcentual entre valores reales y GPS por GRUPO y MARCA\n'
              f'Categoría: {categoria}, Filtro: {tipo_filtro}', 
              fontsize=18, 
              fontweight='bold')
    
    # Obtener los nombres reales de GRUPO y MARCA
    grupo_names = [str(grupo) for grupo in matrix_copy.index[:-1]]  # Excluir 'Total'
    marca_names = [str(marca) for marca in matrix_copy.columns[:-1]]  # Excluir 'Total'
    
    # Aumentar el tamaño de las etiquetas de los ejes
    plt.ylabel('GRUPO', fontsize=14)
    plt.xlabel('MARCA', fontsize=14)
    
    # Personalizar etiquetas para incluir los nombres reales
    # Importante: Para los yticks, usamos rotation=0 para que sean horizontales
    plt.yticks(np.arange(len(matrix_copy.index)), labels=matrix_copy.index, fontsize=12, rotation=0)
    plt.xticks(np.arange(len(matrix_copy.columns)), labels=matrix_copy.columns, fontsize=12, rotation=45, ha='right')
    
    # Ajustar márgenes para evitar recortes
    plt.tight_layout()
    return plt.gcf()  # Devolver la figura actual

