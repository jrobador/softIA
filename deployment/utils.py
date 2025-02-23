import os
import logging

def get_latest_model_path(model_dir: str) -> str:
    """
    Obtiene la ruta del modelo ajustado más reciente basado en la fecha de modificación.
    
    Args:
        model_dir (str): Directorio que contiene los modelos ajustados.
    
    Returns:
        str: Ruta del directorio del modelo más reciente.
    
    Raises:
        FileNotFoundError: Si no se encuentran modelos en el directorio.
    """
    logger = logging.getLogger(__name__)
    if not os.path.exists(model_dir):
        logger.error(f"El directorio de modelos {model_dir} no existe.")
        raise FileNotFoundError(f"El directorio de modelos {model_dir} no existe.")
    
    subdirectorios = [os.path.join(model_dir, d) for d in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, d))]
    if not subdirectorios:
        logger.error(f"No se encontraron modelos ajustados en {model_dir}.")
        raise FileNotFoundError(f"No se encontraron modelos ajustados en {model_dir}.")
    
    directorio_mas_reciente = max(subdirectorios, key=os.path.getmtime)
    logger.info(f"Directorio del modelo más reciente: {directorio_mas_reciente}")
    return directorio_mas_reciente
