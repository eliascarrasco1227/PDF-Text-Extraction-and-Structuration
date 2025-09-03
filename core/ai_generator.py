# Updated ai_generator.py
from google import genai
from google.genai import types
from .pdf_processor import PDFProcessor
from config.paths import PAGINAS, ALL_PAGES
from PyPDF2 import PdfReader

class AIGenerator:
    def __init__(self, model: str = 'gemini-2.5-flash', pages_per_block: int = 5):
        self.client = genai.Client()
        self.model = model
        self.pdf_processor = PDFProcessor()
        self.pages_per_block = pages_per_block
    
    def _get_total_pages(self, pdf_path: str) -> int:
        """Obtiene el número total de páginas del PDF"""
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            return len(pdf.pages)
    
    def generate_from_pdf(self, pdf_path: str, prompt: str) -> str:
        """Genera respuesta con estructura XML por bloques de páginas"""
        # Determinar el rango de páginas a procesar
        if ALL_PAGES:
            # Procesar todas las páginas del PDF
            total_pdf_pages = self._get_total_pages(pdf_path)
            start_page, end_page = 1, total_pdf_pages
            print(f"📄 Procesando TODAS las páginas del PDF (1-{total_pdf_pages})")
        else:
            # Procesar solo el rango especificado en PAGINAS
            start_page, end_page = PAGINAS
            print(f"📄 Procesando páginas {start_page}-{end_page}")
        
        start_page = max(1, start_page)  # Asegurar que la página inicial es al menos 1 
        all_responses = []
        
        # Calcular el total de páginas a procesar
        total_pages_to_process = end_page - start_page + 1
        
        # Process pages in blocks to avoid timeout
        current_page = start_page
        processed_pages = 0
        
        while current_page <= end_page:
            # Calcular el final del bloque CORRECTAMENTE
            block_end = min(current_page + self.pages_per_block, end_page + 1)  # +1 para inclusivo
            pages_in_block = block_end - current_page
            
            print(f"Processing pages {current_page} to {block_end - 1} ({pages_in_block} pages)...")
            
            # Extraer las páginas (current_page hasta block_end - 1, inclusive)
            pdf_bytes = self.pdf_processor.extract_pages(pdf_path, (current_page, block_end))
            
            # Modificamos el prompt para incluir estructura XML
            xml_prompt = f"""Genera un análisis XML donde:
    1. Cada página vaya dentro de <pagina num="N">. Las páginas a extraer son de la {current_page} a la {block_end - 1}.
    2. Incluye metadatos del documento (el titulo {pdf_path} y las páginas procesadas).
    3. Extrae TODO el texto literalmente SIN EXCEPCIONES.
    4. NUNCA generes comentarios explicativos.
    5. El texto original debe ir dentro de <contenido>

    {prompt}"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(
                        data=pdf_bytes,
                        mime_type='application/pdf',
                    ),
                    xml_prompt
                ]
            )
            all_responses.append(response.text)
            
            # Actualizar contador de páginas procesadas
            processed_pages += pages_in_block
            
            # Calcular porcentaje completado
            percentage = int((processed_pages / total_pages_to_process) * 100)
            
            # Crear barra de progreso
            bar_length = 10
            filled_length = int(bar_length * percentage / 100)
            bar = '█' * filled_length + '▒' * (bar_length - filled_length)
            
            # Mostrar progreso
            print(f"{bar} {percentage}%")
            print("---------------------------------")
            
            # Move to next block CORRECTAMENTE
            current_page = block_end
        
        # Combine all responses
        return "\n".join(all_responses)