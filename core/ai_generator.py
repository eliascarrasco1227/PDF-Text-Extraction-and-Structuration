from google import genai
from google.genai import types
from google.genai.errors import ServerError
from .pdf_processor import PDFProcessor
from config.properties import (
    PAGINAS, ALL_PAGES, RETRY_DELAY, MAX_RETRIES, 
    FEW_SHOT_PDF_PATH, FEW_SHOT_XML_PATH,
    FEW_SHOT_PDF_PATH_2, FEW_SHOT_XML_PATH_2, 
    USE_FEW_SHOT,
    GEMINI_MODEL,
    DTD_PATH
)
from PyPDF2 import PdfReader
from validator.xml_validator import XMLValidator
from core.xml_corrector import XMLCorrector
from core.logger_config import app_logger
import time
import os
import re

class AIGenerator:
    # He cambiado el default a 1.5-flash para intentar evitar el error 429 desde el inicio
    def __init__(self, model: str = GEMINI_MODEL, pages_per_block: int = 5, temperature: float = 0.1):
        self.client = genai.Client()
        self.model = model
        self.pdf_processor = PDFProcessor()
        self.pages_per_block = pages_per_block
        self.logger = app_logger
        self.retry_delay = RETRY_DELAY
        self.max_retries = MAX_RETRIES
        self.temperature = temperature
        self.few_shot_examples = self._load_few_shot_data() if USE_FEW_SHOT else []
        self.corrector = XMLCorrector() 
        self.validator = XMLValidator()

    def _load_few_shot_data(self) -> list:
        examples = []
        self.logger.info("🧠 Cargando ejemplos Few-Shot...")

        example_configs = [
            {"pdf": FEW_SHOT_PDF_PATH, "xml": FEW_SHOT_XML_PATH, "name": "Ejemplo 1 (Kaqchikel)"},
            {"pdf": FEW_SHOT_PDF_PATH_2, "xml": FEW_SHOT_XML_PATH_2, "name": "Ejemplo 2 (Mam)"}
        ]

        for config in example_configs:
            try:
                if not os.path.exists(config["pdf"]):
                    continue
                if not os.path.exists(config["xml"]):
                    continue

                with open(config["pdf"], "rb") as f:
                    pdf_bytes = f.read()
                with open(config["xml"], "r", encoding="utf-8") as f:
                    xml_text = f.read()

                examples.append({
                    "pdf": pdf_bytes, "xml": xml_text, "name": config["name"]
                })
                self.logger.info(f"✅ {config['name']} cargado correctamente.")
            except Exception as e:
                self.logger.error(f"❌ Error cargando {config['name']}: {str(e)}")

        self.logger.info(f"🧠 Total ejemplos cargados: {len(examples)}")
        return examples

    def _get_total_pages(self, pdf_path: str) -> int:
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            return len(pdf.pages)
        
    def _determine_page_range(self, pdf_path: str) -> tuple:
        total_pdf_pages = self._get_total_pages(pdf_path)

        if ALL_PAGES:
            start_page, end_page = 1, total_pdf_pages
            self.logger.info(f"📄 Procesando TODAS las páginas del PDF (1-{total_pdf_pages})")
        else:
            start_page, end_page = PAGINAS
            self.logger.info(f"📄 Procesando páginas {start_page}-{end_page}")
            start_page = max(1, start_page)
            end_page = min(total_pdf_pages, end_page)
        
        return start_page, end_page
    
    def _pretty_print_progress(self, processed_pages: int, total_pages_to_process: int):
        percentage = int((processed_pages / total_pages_to_process) * 100)
        bar_length = 10
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '▒' * (bar_length - filled_length)
        self.logger.info(f"{bar} {percentage}%")
        self.logger.info("---------------------------------")
    
    def _clean_xml_response(self, text: str) -> str:
            """Elimina posibles bloques de código markdown (```xml ... ```)"""
            clean_text = re.sub(r'```xml\s*', '', text)
            clean_text = re.sub(r'```\s*', '', clean_text)
            return clean_text.strip()

    def _generate_content_with_retry(self, target_pdf_bytes: bytes, prompt: str) -> str:
        contents = []
        # Carga de Few-Shot 
        if self.few_shot_examples:
            contents.append("INSTRUCCIONES DE ENTRENAMIENTO (FEW-SHOT):")
            contents.append("A continuación se presentan ejemplos de documentos PDF y sus transcripciones XML correctas. Úsalos como referencia estricta de formato y estructura.")
            for i, example in enumerate(self.few_shot_examples):
                contents.append(f"--- INICIO EJEMPLO {i + 1} ({example['name']}) ---")
                contents.append(types.Part.from_bytes(data=example["pdf"], mime_type='application/pdf'))
                contents.append(f"SALIDA XML CORRECTA PARA EJEMPLO {i + 1}:")
                contents.append(example["xml"])
                contents.append(f"--- FIN EJEMPLO {i + 1} ---")
            contents.append("TAREA ACTUAL: Ahora procesa el siguiente documento PDF aplicando la misma lógica, estructura y formato XML que en los ejemplos anteriores.")
        else:
            contents.append("Procesa el siguiente documento PDF:")

        contents.append(types.Part.from_bytes(data=target_pdf_bytes, mime_type='application/pdf'))
        contents.append(prompt)

        # --- BUCLE DE REINTENTOS CON VALIDACIÓN ---
        """Bucle de reintentos con flujo de corrección"""
        
        # Cargamos el DTD una vez para pasárselo al corrector
        with open(DTD_PATH, 'r', encoding='utf-8') as f:
            dtd_content = f.read()

        xml_candidato = ""
        error_detallado = ""

        for attempt in range(self.max_retries):
            try:
                # PASO 1: Obtener el XML (Generación inicial o Corrección)
                if attempt == 0:
                    self.logger.info(f"📡 Generando XML inicial...")
                    # Llamada original a Gemini
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=contents,
                        config=types.GenerateContentConfig(temperature=self.temperature)
                    )
                    xml_candidato = self._clean_xml_response(response.text)
                else:
                    self.logger.warning(f"🔧 Intento {attempt + 1}: XML no válido. Llamando al Corrector...")
                    # Llamada al segundo LLM especializado en corregir
                    xml_candidato = self.corrector.fix_xml(
                        faulty_xml=xml_candidato,
                        error_message=error_detallado,
                        dtd_content=dtd_content,
                        pdf_bytes=target_pdf_bytes
                    )
                    xml_candidato = self._clean_xml_response(xml_candidato)

                # PASO 2: Validar el XML resultante
                codigo, mensaje = self.validator.check_valid(xml_candidato, DTD_PATH)

                if codigo == 1:
                    self.logger.info(f"✅ XML validado correctamente en el intento {attempt + 1}.")
                    return xml_candidato
                else:
                    # Guardamos el error para el siguiente intento del corrector
                    error_detallado = mensaje
                    self.logger.error(f"❌ Validación fallida: {mensaje}")
                    time.sleep(self.retry_delay)

            except ServerError as e:
                if "503" in str(e) and attempt < self.max_retries - 1:
                    self.logger.warning(f"⚠️ Servidor sobrecargado. Reintentando... ({attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    continue
                else: raise
            except Exception as e:
                raise
        
        self.logger.warning(f"⚠️ No se pudo obtener un XML válido tras {self.max_retries} intentos.")
        self.logger.warning(f"📄 Se devolverá el último XML generado para no detener el proceso.")
        
        return xml_candidato # Devolvemos lo que tengamos, aunque no sea válido
    
        #raise Exception(f"❌ No se pudo obtener un XML válido después de {self.max_retries} intentos.")
    
    def generate_from_pdf(self, pdf_path: str, prompt: str) -> str:
        start_page, end_page = self._determine_page_range(pdf_path)
        all_responses = []
        total_pages_to_process = end_page - start_page + 1
        current_page = start_page
        processed_pages = 0
        
        while current_page <= end_page:
            block_end = min(current_page + self.pages_per_block, end_page + 1)
            pages_in_block = block_end - current_page
            
            self.logger.info(f"📖 Procesando páginas {current_page} a {block_end - 1} ({pages_in_block} páginas)...")
            
            pdf_bytes = self.pdf_processor.extract_pages(pdf_path, (current_page, block_end))
            
            xml_prompt = f"""Genera un análisis XML donde:
Cada página vaya dentro de <pagina num="N">. Las páginas a extraer son de la {current_page} a la {block_end - 1}.

{prompt}"""
            
            try:
                response_text = self._generate_content_with_retry(pdf_bytes, xml_prompt)
                all_responses.append(response_text)
                
                processed_pages += pages_in_block
                self._pretty_print_progress(processed_pages, total_pages_to_process)
                
            except Exception as e:
                error_msg = str(e)
                # DETECCION DE ERROR DE CUOTA (LIMPIEZA DE LOGS)
                if "RESOURCE_EXHAUSTED" in error_msg:
                    # Parseamos el límite para mostrarlo
                    limit_match = re.search(r"limit: (\d+)", error_msg)
                    if not limit_match:
                         limit_match = re.search(r"quotaValue': '(\d+)'", error_msg)
                    limit = limit_match.group(1) if limit_match else "?"
                    
                    self.logger.error(f"🚫 Superaste el limite de uso de gemini de tu versión, recuerda que el limite diario es {limit}")
                    
                    # Lanzamos el error para que main lo atrape y pare el programa
                    raise e 
                
                elif "503" in error_msg:
                    self.logger.error(f"❌ Error crítico: Servidor sobrecargado después de {self.max_retries} intentos.")
                    raise
                else:
                    self.logger.error(f"❌ Error inesperado: {error_msg}")
                    raise
            
            current_page = block_end
        
        return "\n".join(all_responses)