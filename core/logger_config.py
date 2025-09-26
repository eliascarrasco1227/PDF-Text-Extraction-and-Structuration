# core/logger_config.py
import logging
import os
from datetime import datetime
from config.properties import LOG_DIR

def setup_logging():
    """Configura el sistema de logging de la aplicación"""
    
    # Crear directorio de logs si no existe
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Nombre del archivo de log con timestamp en el formato deseado
    date_part = datetime.now().strftime("%Y-%m-%d")
    time_part = datetime.now().strftime("%H-%M-%S")
    log_filename = f"application_date_{date_part}_time_{time_part}.log"
    log_path = os.path.join(LOG_DIR, log_filename)
    
    # Configurar formato para archivo (completo)
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar formato para consola (limpio)
    console_format = '%(message)s'
    
    # Crear logger
    logger = logging.getLogger('pdf_processor')
    logger.setLevel(logging.INFO)
    
    # Eliminar handlers existentes si los hay
    logger.handlers.clear()
    
    # Handler para archivo (formato completo)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(file_format, date_format))
    
    # Handler para consola (formato limpio)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(console_format))
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logging configurado. Archivo: {log_path}")
    
    return logger

# Logger global
app_logger = setup_logging()