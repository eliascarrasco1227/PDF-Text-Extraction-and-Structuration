# Updated ai_generator.py
from google import genai
from google.genai import types
from .pdf_processor import PDFProcessor
from config.paths import PAGINAS

class AIGenerator:
    def __init__(self, model: str = 'gemini-2.5-flash', pages_per_block: int = 5):
        self.client = genai.Client()
        self.model = model
        self.pdf_processor = PDFProcessor()
        self.pages_per_block = pages_per_block
    
    def generate_from_pdf(self, pdf_path: str, prompt: str) -> str:
        """Genera respuesta con estructura XML por bloques de páginas"""
        start_page, end_page = PAGINAS
        start_page = max(1, start_page)  # Asegurar que la página inicial es al menos 1 
        all_responses = []
        
        # Process pages in blocks to avoid timeout
        current_page = start_page
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
            
            # Move to next block CORRECTAMENTE
            current_page = block_end
        
        # Combine all responses
        return "\n".join(all_responses)