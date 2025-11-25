# Configuración editable
#PDF_PATH = 'data/Gramatica-Normativa-Mam.pdf'
#PDF_PATH = 'data/few-shot/Gramatica-Normativa-Kaqchikel_pag_146.pdf'
#PDF_PATH = 'data/reducidos/Gramatica-Normativa-Kaqchikel_pag_172.pdf'
PDF_PATH = 'data/Gramatica-Normativa-Kiche.pdf'
PROMPT_PATH = 'prompts/prompt_v4'
OUTPUT_DIR = 'output'
LOG_DIR = 'logs'  # directorio de logs
ALL_PAGES = False  # Si es True, procesa todas las páginas del PDF ignorando PAGINAS
PAGINAS = (43, 43)  # Páginas a procesar (inicio, fin), ambas inclusive.  (primera página = 0. pagina = las que indica el pdf - 1)
PAGES_PER_BLOCK = 5  # Número de páginas a procesar por bloque

# Configuración para reintentos
RETRY_DELAY = 15  # Segundos a esperar entre reintentos (para errores 503, servidor de gemini colapsado)
MAX_RETRIES = 5    # Número máximo de reintentos


# Few shot
FEW_SHOT_PDF_PATH = 'data/few-shot/Gramatica-Normativa-Kaqchikel_pag_146.pdf'
FEW_SHOT_XML_PATH = 'data/few-shot/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml'

# Interruptor para activar/desactivar el few-shot si quieres probar sin él
USE_FEW_SHOT = True

# Evaluator
# Las variables de evaluator están en evaluator/properties.py