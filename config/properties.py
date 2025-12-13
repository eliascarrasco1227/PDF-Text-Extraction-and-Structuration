# Configuración editable
#PDF_PATH = 'data/Gramatica-Normativa-Mam.pdf'
#PDF_PATH = 'data/few-shot/Gramatica-Normativa-Kaqchikel_pag_146.pdf'
#PDF_PATH = 'data/reducidos/Gramatica-Normativa-Kaqchikel_pag_172.pdf'
#PDF_PATH = 'data/Gramatica-Normativa-Kaqchikel.pdf'
#PDF_PATH = 'data/Gramatica-Normativa-Kiche.pdf'
PDF_PATH = 'data/reducidos/Gramatica-Normativa-Kiche_pag_44.pdf'
PROMPT_PATH = 'prompts/prompt_v4'
OUTPUT_DIR = 'output'
LOG_DIR = 'logs'  # directorio de logs
ALL_PAGES = True  # Si es True, procesa todas las páginas del PDF ignorando PAGINAS
PAGINAS = (146, 146)  # Páginas a procesar (inicio, fin), ambas inclusive.  (primera página = 0. pagina = las que indica el pdf - 1)
PAGES_PER_BLOCK = 5  # Número de páginas a procesar por bloque

# Configuración para reintentos
RETRY_DELAY = 15  # Segundos a esperar entre reintentos (para errores 503, servidor de gemini colapsado)
MAX_RETRIES = 5    # Número máximo de reintentos

# Few shot
# Interruptor para activar/desactivar el few-shot
USE_FEW_SHOT = True 

# Ejemplo 1 (Kaqchikel)
FEW_SHOT_PDF_PATH = 'data/few-shot/Gramatica-Normativa-Kaqchikel_pag_146.pdf'
FEW_SHOT_XML_PATH = 'data/few-shot/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml'

# Ejemplo 2 (Mam) 
FEW_SHOT_PDF_PATH_2 = 'data/few-shot/Gramatica-Normativa-Mam_pag_80.pdf'
FEW_SHOT_XML_PATH_2 = 'data/few-shot/Gramatica-Normativa-Mam_páginas_80-80.xml'


# Temperatura: 0.0 = Deterministico (Mejor para extracción fiel). 1.0 = Creativo. (default in gemini 1.0, balanced) 
TEMPERATURE = 0.0

GEMINI_MODEL = 'gemini-2.5-flash-lite'  # Modelo de Gemini a usar



# Evaluator
# Las variables de evaluator están en evaluator/properties.py