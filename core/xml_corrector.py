# core/xml_corrector.py
from google import genai
from google.genai import types
import os
from core.logger_config import app_logger

class XMLCorrector:
    """
    Especialista en corregir XMLs que no cumplen el DTD.
    Usa un modelo superior (Pro) para asegurar la validez estructural.
    """
    def __init__(self, model: str = "gemma-3-27b-it"):
        self.client = genai.Client()
        self.model = model
        self.logger = app_logger

    def fix_xml(self, faulty_xml: str, error_message: str, dtd_content: str, pdf_bytes: bytes) -> str:
        """
        Llamada al LLM para corregir el XML basándose en el error y el DTD.
        """
        prompt = f"""
        ERES UN EXPERTO EN DEPURACIÓN XML Y FILOLOGÍA MAYA.
        
        TAREA: Has generado un XML que no cumple con las reglas del DTD proporcionado.
        Debes corregirlo para que sea 100% VÁLIDO y esté BIEN FORMADO.

        CONTEXTO DEL ERROR:
        {error_message}

        REGLAS DEL DTD (Gramática estricta):
        {dtd_content}

        XML DEFECTUOSO A CORREGIR:
        {faulty_xml}

        INSTRUCCIONES DE CORRECCIÓN:
        1. NO añadas ni quites información lingüística, solo arregla las etiquetas y la estructura.
        2. Asegúrate de que todos los elementos (unit, form, gloss, etc.) estén correctamente anidados.
        3. Si falta el análisis sintáctico y el DTD lo requiere, genéralo basándote en el contenido.
        4. DEVUELVE ÚNICAMENTE EL CÓDIGO XML LIMPIO. SIN MARKDOWN, SIN EXPLICACIONES.
        """

        try:
            contents = [
                types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'),
                prompt
            ]

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.0, # Mínima creatividad para correcciones técnicas
                    top_p=0.1
                )
            )
            
            if not response.text:
                return faulty_xml
                
            return response.text
        except Exception as e:
            self.logger.error(f"❌ Error en el proceso de corrección: {str(e)}")
            return faulty_xml