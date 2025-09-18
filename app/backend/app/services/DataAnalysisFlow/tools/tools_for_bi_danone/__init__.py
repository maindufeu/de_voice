from typing import Dict, Any

from .building_blocks import get_top_building_blocks_dict, get_top_building_blocks, crear_grafico_cascada_dict, crear_grafico_cascada
from .innos import get_innos_gps_dict, get_innos_gps, crear_grafica_top10_innos_gps_dict, crear_grafica_top10_innos_gps
from .mape_gps_heatmap import create_grupo_marca_matrix_dict, create_grupo_marca_matrix, create_heatmap_with_totals_dict, create_heatmap_with_totals
from .quarter_comparation import get_pivoted_df_dict, get_pivoted_df, compare_real_years_dict, compare_real_years, compare_real_vs_predicted_dict, compare_real_vs_predicted, crear_grafica_comparacion_dict, crear_grafica_comparacion
from .sku_growth_pareto import analyze_sku_pareto_dict, analyze_sku_pareto, crear_grafica_pareto_dict, crear_grafica_pareto, analyze_sku_growth_dict, analyze_sku_growth
from .seasonality import get_seasonality_dict, get_seasonality, crear_grafica_variacion_dict, crear_grafica_variacion



def get_all_paired_tools() -> Dict[str, Dict[str, Any]]:
    """
    Devuelve un diccionario con todas las funciones y sus descripciones.
    
    Returns:
    --------
    dict
        Diccionario con las funciones y sus descripciones.
    """
    return [
        (create_grupo_marca_matrix_dict, create_grupo_marca_matrix),
        (create_heatmap_with_totals_dict, create_heatmap_with_totals),
        (get_pivoted_df_dict, get_pivoted_df),
        (compare_real_years_dict, compare_real_years),
        (compare_real_vs_predicted_dict, compare_real_vs_predicted),
        (crear_grafica_comparacion_dict, crear_grafica_comparacion),
        (analyze_sku_pareto_dict, analyze_sku_pareto),
        (crear_grafica_pareto_dict, crear_grafica_pareto),
        (analyze_sku_growth_dict, analyze_sku_growth),
        (get_top_building_blocks_dict, get_top_building_blocks),
        (crear_grafico_cascada_dict, crear_grafico_cascada),
        (get_seasonality_dict, get_seasonality),
        (crear_grafica_variacion_dict, crear_grafica_variacion),
        (get_innos_gps_dict, get_innos_gps),
        (crear_grafica_top10_innos_gps_dict, crear_grafica_top10_innos_gps)
    ]