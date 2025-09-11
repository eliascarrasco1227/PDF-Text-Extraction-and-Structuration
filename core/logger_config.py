# core/logger_config.py
import logging
import os
from datetime import datetime
from config.paths import LOG_DIR

def setup_logging():
    """Configura el sistema de logging de la aplicación"""
    
    # Crear directorio de logs si no existe
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Nombre del archivo de log con timestamp en el formato deseado
    date_part = datetime.now().strftime("%Y-%m-%d")
    time_part = datetime.now().strftime("%H-%M-%S")
    log_filename = f"application_date_{date_part}_time_{time_part}.log"
    log_path = os.path.join(LOG_DIR, log_filename)
    
    # Configurar formato
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()  # También mostrar en consola
        ]
    )
    
    # Logger específico para la aplicación
    logger = logging.getLogger('pdf_processor')
    logger.info(f"Logging configurado. Archivo: {log_path}")
    
    return logger

# Logger global
app_logger = setup_logging()