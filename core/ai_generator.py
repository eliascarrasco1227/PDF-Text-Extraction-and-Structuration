# core/ai_generator.py
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from .pdf_processor import PDFProcessor
from config.properties import PAGINAS, ALL_PAGES, RETRY_DELAY, MAX_RETRIES, FEW_SHOT_PDF_PATH, FEW_SHOT_XML_PATH, USE_FEW_SHOT
from PyPDF2 import PdfReader
from core.logger_config import app_logger
import time
import os

class AIGenerator:
    def __init__(self, model: str = 'gemini-2.5-flash', pages_per_block: int = 5):
        self.client = genai.Client()
        self.model = model
        self.pdf_processor = PDFProcessor()
        self.pages_per_block = pages_per_block
        self.logger = app_logger
        self.retry_delay = RETRY_DELAY
        self.max_retries = MAX_RETRIES
        
        # Cargar datos Few-Shot en memoria al iniciar
        self.few_shot_data = self._load_few_shot_data() if USE_FEW_SHOT else None

    def _load_few_shot_data(self):
        """Carga los archivos de ejemplo en memoria una sola vez"""
        try:
            self.logger.info("🧠 Cargando datos de ejemplo (Few-Shot)...")
            
            # Cargar PDF de ejemplo
            if not os.path.exists(FEW_SHOT_PDF_PATH):
                raise FileNotFoundError(f"No se encuentra el PDF de ejemplo: {FEW_SHOT_PDF_PATH}")
            with open(FEW_SHOT_PDF_PATH, "rb") as f:
                pdf_bytes = f.read()

            # Cargar Respuesta XML de ejemplo
            if not os.path.exists(FEW_SHOT_XML_PATH):
                raise FileNotFoundError(f"No se encuentra el XML de ejemplo: {FEW_SHOT_XML_PATH}")
            with open(FEW_SHOT_XML_PATH, "r", encoding="utf-8") as f:
                xml_text = f.read()

            self.logger.info("✅ Datos Few-Shot cargados correctamente.")
            return {"pdf": pdf_bytes, "xml": xml_text}

        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo cargar el Few-Shot, se procederá sin él. Error: {e}")
            return None

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
    
    def _generate_content_with_retry(self, target_pdf_bytes: bytes, prompt: str) -> str:
        """Genera contenido construyendo un prompt multimodal con Few-Shot"""
        
        # Construcción de la lista de contenidos (Prompt Engineering)
        contents = []

        # 1. Inyectar Few-Shot (si está disponible)
        if self.few_shot_data:
            contents.append("INSTRUCIONES DE ENTRENAMIENTO (FEW-SHOT):")
            contents.append("A continuación se presenta un documento PDF de EJEMPLO y su transcripción XML CORRECTA. Úsalo únicamente como referencia de formato y estilo. NO extraigas contenido de este ejemplo en tu respuesta final.")
            
            # PDF Ejemplo
            contents.append(types.Part.from_bytes(
                data=self.few_shot_data["pdf"],
                mime_type='application/pdf'
            ))
            
            # Respuesta Ejemplo
            contents.append("SALIDA XML ESPERADA PARA EL EJEMPLO ANTERIOR:")
            contents.append(self.few_shot_data["xml"])
            
            contents.append("--- FIN DEL EJEMPLO ---")
            contents.append("TAREA ACTUAL: Ahora procesa el siguiente documento PDF aplicando la misma lógica y formato que en el ejemplo anterior.")

        else:
            # Fallback si no hay few-shot
            contents.append("Procesa el siguiente documento PDF:")

        # 2. Inyectar el PDF Objetivo (Target)
        contents.append(types.Part.from_bytes(
            data=target_pdf_bytes,
            mime_type='application/pdf'
        ))

        # 3. Inyectar el Prompt de instrucciones
        contents.append(prompt)

        for attempt in range(self.max_retries):
            try:
                # Llamada a la API con la lista de contenidos estructurada
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents
                )
                return response.text
                
            except ServerError as e:
                if "503" in str(e) and attempt < self.max_retries - 1:
                    self.logger.warning(f"⚠️  Servidor sobrecargado (503). Reintentando en {self.retry_delay} segundos... (Intento {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise
            except Exception as e:
                raise
        
        raise ServerError("No se pudo completar la solicitud después de todos los reintentos")
    
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
            
            # Extraer las páginas del PDF objetivo
            pdf_bytes = self.pdf_processor.extract_pages(pdf_path, (current_page, block_end))
            
            # Prompt específico para el bloque
            xml_prompt = f"""Genera un análisis XML donde:
Cada página vaya dentro de <pagina num="N">. Las páginas a extraer son de la {current_page} a la {block_end - 1}.

{prompt}"""
            
            try:
                response_text = self._generate_content_with_retry(pdf_bytes, xml_prompt)
                all_responses.append(response_text)
                
                processed_pages += pages_in_block
                self._pretty_print_progress(processed_pages, total_pages_to_process)
                
            except ServerError as e:
                if "503" in str(e):
                    self.logger.error(f"❌ Error crítico: Servidor sobrecargado después de {self.max_retries} intentos.")
                raise
            except Exception as e:
                self.logger.error(f"❌ Error inesperado: {str(e)}")
                raise
            
            current_page = block_end
        
        return "\n".join(all_responses)