# Configuración editable
PDF_PATH = 'data/Gramatica-Normativa-Kiche.pdf'
PROMPT_PATH = 'prompts/prompt_v3'
OUTPUT_DIR = 'output'
LOG_DIR = 'logs'  # directorio de logs
ALL_PAGES = False  # Si es True, procesa todas las páginas del PDF ignorando PAGINAS
PAGINAS = (43, 43)  # Páginas a procesar (inicio, fin), ambas inclusive.  (primera página = 0. pagina = las que indica el pdf - 1)
PAGES_PER_BLOCK = 5  # Número de páginas a procesar por bloque

# Configuración para reintentos
RETRY_DELAY = 15  # Segundos a esperar entre reintentos (para errores 503, servidor de gemini colapsado)
MAX_RETRIES = 5    # Número máximo de reintentos



# Evaluator
# Las variables de evaluator están en evaluator/properties.py