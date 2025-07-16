from google import genai
from google.genai import types
from .pdf_processor import PDFProcessor

class AIGenerator:
    def __init__(self, model: str = 'gemini-2.5-flash'):
        self.client = genai.Client()
        self.model = model
        self.pdf_processor = PDFProcessor()
    
    def generate_from_pdf(self, pdf_path: str, prompt: str, page_range: tuple) -> str:
        """Genera respuesta usando solo las páginas especificadas"""
        pdf_bytes = self.pdf_processor.extract_pages(pdf_path, page_range)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type='application/pdf'
                ),
                prompt
            ]
        )
        return response.text