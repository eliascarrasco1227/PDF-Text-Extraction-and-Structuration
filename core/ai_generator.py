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
        self.pages_per_block = pages_per_block  # Number of pages to process at once
    
    def generate_from_pdf(self, pdf_path: str, prompt: str) -> str:
        """Genera respuesta con estructura XML por bloques de páginas"""
        start_page, end_page = PAGINAS
        all_responses = []
        
        # Process pages in blocks to avoid timeout
        for block_start in range(start_page, end_page + 1, self.pages_per_block):
            block_end = min(block_start + self.pages_per_block - 1, end_page)
            
            print(f"Processing pages {block_start} to {block_end}...")
            
            pdf_bytes = self.pdf_processor.extract_pages(pdf_path, (block_start, block_end))
            
            # Modificamos el prompt para incluir estructura XML
            xml_prompt = f"""Genera un análisis XML donde:
1. Cada página vaya dentro de <pagina num="N">. Las páginas a extraer son de la {block_start} a la {block_end}.
2. Incluye metadatos del documento (el titulo {pdf_path} y las páginas procesadas).
3. El texto original debe ir dentro de <contenido>

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
        
        # Combine all responses
        return "\n".join(all_responses)