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
    OUTPUT_FORMAT  # <--- Nueva propiedad necesaria en config/properties.py
)
from PyPDF2 import PdfReader
from core.logger_config import app_logger
import time
import os
import re

class AIGenerator:
    def __init__(self, model: str = GEMINI_MODEL, pages_per_block: int = 5, temperature: float = 0.1):
        self.client = genai.Client()
        self.model = model
        self.pdf_processor = PDFProcessor()
        self.pages_per_block = pages_per_block
        self.logger = app_logger
        self.retry_delay = RETRY_DELAY
        self.max_retries = MAX_RETRIES
        self.temperature = temperature
        self.output_format = OUTPUT_FORMAT.lower() # "xml" o "json"
        
        self.few_shot_examples = self._load_few_shot_data() if USE_FEW_SHOT else []

    def _load_few_shot_data(self) -> list:
        examples = []
        self.logger.info(f"🧠 Cargando ejemplos Few-Shot (Modo: {self.output_format.upper()})...")

        example_configs = [
            {"pdf": FEW_SHOT_PDF_PATH, "ref": FEW_SHOT_XML_PATH, "name": "Ejemplo 1"},
            {"pdf": FEW_SHOT_PDF_PATH_2, "ref": FEW_SHOT_XML_PATH_2, "name": "Ejemplo 2"}
        ]

        for config in example_configs:
            try:
                if not os.path.exists(config["pdf"]) or not os.path.exists(config["ref"]):
                    continue

                with open(config["pdf"], "rb") as f:
                    pdf_bytes = f.read()
                with open(config["ref"], "r", encoding="utf-8") as f:
                    ref_text = f.read()

                examples.append({
                    "pdf": pdf_bytes, "ref": ref_text, "name": config["name"]
                })
                self.logger.info(f"✅ {config['name']} cargado.")
            except Exception as e:
                self.logger.error(f"❌ Error cargando {config['name']}: {str(e)}")

        return examples

    def _get_total_pages(self, pdf_path: str) -> int:
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            return len(pdf.pages)
        
    def _determine_page_range(self, pdf_path: str) -> tuple:
        total_pdf_pages = self._get_total_pages(pdf_path)
        if ALL_PAGES:
            return 1, total_pdf_pages
        
        start_page, end_page = PAGINAS
        return max(1, start_page), min(total_pdf_pages, end_page)
    
    def _generate_content_with_retry(self, target_pdf_bytes: bytes, prompt: str) -> str:
        contents = []

        # Configuración de los contenidos del prompt
        header = "INSTRUCCIONES DE ENTRENAMIENTO:"
        format_instruction = f"referencia estricta de formato y estructura {self.output_format.upper()}."
        
        if self.few_shot_examples:
            contents.append(header)
            contents.append(f"A continuación se presentan ejemplos de documentos PDF y sus salidas {self.output_format.upper()} correctas. Úsalos como {format_instruction}")
            for i, example in enumerate(self.few_shot_examples):
                contents.append(f"--- INICIO EJEMPLO {i + 1} ---")
                contents.append(types.Part.from_bytes(data=example["pdf"], mime_type='application/pdf'))
                contents.append(f"SALIDA CORRECTA ({self.output_format.upper()}):")
                contents.append(example["ref"])
                contents.append(f"--- FIN EJEMPLO {i + 1} ---")
            contents.append(f"TAREA ACTUAL: Procesa el siguiente PDF aplicando la lógica y formato {self.output_format.upper()} de los ejemplos.")
        else:
            contents.append(f"Procesa el siguiente PDF y genera una estructura {self.output_format.upper()}:")

        contents.append(types.Part.from_bytes(data=target_pdf_bytes, mime_type='application/pdf'))
        contents.append(prompt)

        # Configuración dinámica de la respuesta (JSON vs XML)
        mime_type = "application/json" if self.output_format == "json" else "text/plain"

        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=self.temperature,
                        response_mime_type=mime_type  # <--- CRÍTICO: Activa el modo JSON nativo
                    )
                )
                return response.text
                
            except ServerError as e:
                if "503" in str(e) and attempt < self.max_retries - 1:
                    self.logger.warning(f"⚠️ Servidor sobrecargado. Reintento {attempt + 1}/{self.max_retries}")
                    time.sleep(self.retry_delay)
                    continue
                raise
            except Exception as e:
                raise
        
        raise ServerError("Límite de reintentos alcanzado.")

    def generate_from_pdf(self, pdf_path: str, prompt: str) -> str:
        start_page, end_page = self._determine_page_range(pdf_path)
        all_responses = []
        total_pages_to_process = end_page - start_page + 1
        current_page = start_page
        processed_pages = 0
        
        while current_page <= end_page:
            block_end = min(current_page + self.pages_per_block, end_page + 1)
            pages_in_block = block_end - current_page
            
            self.logger.info(f"📖 Bloque: Páginas {current_page} a {block_end - 1}...")
            pdf_bytes = self.pdf_processor.extract_pages(pdf_path, (current_page, block_end))
            
            # Ajuste de prompt según formato
            if self.output_format == "json":
                fmt_prompt = f"""Genera un JSON que sea una LISTA de objetos, donde cada objeto represente una página.
Estructura de cada objeto: {{"page_number": N, "content": ... }}
Procesa de la página {current_page} a la {block_end - 1}.
{prompt}"""
            else:
                fmt_prompt = f"""Genera un análisis XML donde:
Cada página vaya dentro de <pagina num="N">.
Páginas a extraer: de la {current_page} a la {block_end - 1}.
{prompt}"""
            
            try:
                response_text = self._generate_content_with_retry(pdf_bytes, fmt_prompt)
                all_responses.append(response_text)
                processed_pages += pages_in_block
                
                # Feedback visual
                self._pretty_print_progress(processed_pages, total_pages_to_process)
                
            except Exception as e:
                error_msg = str(e)
                if "RESOURCE_EXHAUSTED" in error_msg:
                    self.logger.error("🚫 Límite de cuota API alcanzado.")
                    raise e 
                raise
            
            current_page = block_end
        
        # Unimos las respuestas. 
        # Nota: Si es JSON, esto generará una serie de objetos JSON. 
        # El método _clean_ai_response en main.py debería encargarse de unificarlos en un array final.
        return "\n".join(all_responses)

    def _pretty_print_progress(self, processed_pages: int, total_pages_to_process: int):
        percentage = int((processed_pages / total_pages_to_process) * 100)
        bar = '█' * (percentage // 10) + '▒' * (10 - (percentage // 10))
        self.logger.info(f"📊 Progreso: [{bar}] {percentage}%")