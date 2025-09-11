# Updated ai_generator.py
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from .pdf_processor import PDFProcessor
from config.paths import PAGINAS, ALL_PAGES, RETRY_DELAY, MAX_RETRIES
from PyPDF2 import PdfReader
from core.logger_config import app_logger
import time

class AIGenerator:
    def __init__(self, model: str = 'gemini-2.5-flash', pages_per_block: int = 5):
        self.client = genai.Client()
        self.model = model
        self.pdf_processor = PDFProcessor()
        self.pages_per_block = pages_per_block
        self.logger = app_logger
        self.retry_delay = RETRY_DELAY
        self.max_retries = MAX_RETRIES
    
    def _get_total_pages(self, pdf_path: str) -> int:
        """Obtiene el número total de páginas del PDF"""
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            return len(pdf.pages)
        
    def _determine_page_range(self, pdf_path: str) -> tuple:
        """Determina el rango de páginas a procesar basado en la configuración"""
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
    
    def _generate_content_with_retry(self, pdf_bytes: bytes, prompt: str) -> str:
        """Genera contenido con reintentos automáticos para errores 503"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Part.from_bytes(
                            data=pdf_bytes,
                            mime_type='application/pdf',
                        ),
                        prompt
                    ]
                )
                return response.text
                
            except ServerError as e:
                if "503" in str(e) and attempt < self.max_retries - 1:
                    self.logger.warning(f"⚠️  Servidor sobrecargado (503). Reintentando en {self.retry_delay} segundos... (Intento {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # Si no es un error 503 o ya hemos agotado los reintentos, relanzamos la excepción
                    raise
            except Exception as e:
                # Para otros tipos de errores, no hacemos reintentos
                raise
        
        # Esto no debería ejecutarse nunca, pero por seguridad
        raise ServerError("No se pudo completar la solicitud después de todos los reintentos")
    
    def generate_from_pdf(self, pdf_path: str, prompt: str) -> str:
        """Genera respuesta con estructura XML por bloques de páginas con reintentos"""
        start_page, end_page = self._determine_page_range(pdf_path)
        all_responses = []
        total_pages_to_process = end_page - start_page + 1
        current_page = start_page
        processed_pages = 0
        
        while current_page <= end_page:
            block_end = min(current_page + self.pages_per_block, end_page + 1)
            pages_in_block = block_end - current_page
            
            self.logger.info(f"📖 Procesando páginas {current_page} a {block_end - 1} ({pages_in_block} páginas)...")
            
            # Extraer las páginas
            pdf_bytes = self.pdf_processor.extract_pages(pdf_path, (current_page, block_end))
            
            # Modificar el prompt para incluir estructura XML
            xml_prompt = f"""Genera un análisis XML donde:
Cada página vaya dentro de <pagina num="N">. Las páginas a extraer son de la {current_page} a la {block_end - 1}.

{prompt}"""
            
            try:
                # Usar el método con reintentos
                response_text = self._generate_content_with_retry(pdf_bytes, xml_prompt)
                all_responses.append(response_text)
                
                # Actualizar contador de páginas procesadas
                processed_pages += pages_in_block
                self._pretty_print_progress(processed_pages, total_pages_to_process)
                
            except ServerError as e:
                if "503" in str(e):
                    self.logger.error(f"❌ Error crítico: Servidor sobrecargado después de {self.max_retries} intentos. Deteniendo ejecución.")
                raise
            except Exception as e:
                self.logger.error(f"❌ Error inesperado durante el procesamiento: {str(e)}")
                raise
            
            # Mover al siguiente bloque
            current_page = block_end
        
        # Combinar todas las respuestas
        return "\n".join(all_responses)