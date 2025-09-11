# Configuración editable
PDF_PATH = 'data/Gramatica-Normativa-Kiche.pdf'
PROMPT_PATH = 'prompts/prompt_v3'
OUTPUT_DIR = 'output'
LOG_DIR = 'logs'  # Nueva variable para directorio de logs
ALL_PAGES = False  # Si es True, procesa todas las páginas del PDF ignorando PAGINAS
PAGINAS = (43, 43)  # Páginas a procesar (inicio, fin), ambas inclusive.  (primera página = 0. pagina = las que indica el pdf - 1)
PAGES_PER_BLOCK = 5  # Número de páginas a procesar por bloque
