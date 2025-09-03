# Configuración editable
PDF_PATH = 'data/Gramatica-Normativa-Mam.pdf'
PROMPT_PATH = 'prompts/prompt_v3'
OUTPUT_DIR = 'output'
ALL_PAGES = False  # Si es True, procesa todas las páginas del PDF ignorando PAGINAS
PAGINAS = (80, 80)  # Páginas a procesar (inicio, fin), ambas inclusive.  (primera página = 0. pagina = las que indica el pdf - 1)
PAGES_PER_BLOCK = 5  # Número de páginas a procesar por bloque
