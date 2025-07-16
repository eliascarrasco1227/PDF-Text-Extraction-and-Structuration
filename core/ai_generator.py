from google import genai
from google.genai import types

class AIGenerator:
    def __init__(self, model: str = 'gemini-2.5-flash'):
        self.client = genai.Client()
        self.model = model
    
    def generate_from_pdf(self, pdf_path: str, prompt: str) -> str:
        """Genera respuesta usando un PDF y prompt"""
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(
                    data=pdf_data,
                    mime_type='application/pdf'
                ),
                prompt
            ]
        )
        return response.text