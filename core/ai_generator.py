from google import genai
from google.genai import types
from .pdf_processor import PDFProcessor
from config.paths import PAGINAS

class AIGenerator:
    def __init__(self, model: str = 'gemini-2.5-flash'):
        self.client = genai.Client()
        self.model = model
        self.pdf_processor = PDFProcessor()
    
    def generate_from_pdf(self, pdf_path: str, prompt: str) -> str:
        """Genera respuesta con estructura XML por página"""
        pdf_bytes = self.pdf_processor.extract_pages(pdf_path, PAGINAS)
        
        # Modificamos el prompt para incluir estructura XML
        xml_prompt = f"""Genera un análisis XML donde:
1. Cada página vaya dentro de <pagina num="N">. Las páginas a extraer son de la {PAGINAS[0]} a la {PAGINAS[1]}.
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
        return response.text