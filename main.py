# main.py
from config.properties import (
    PDF_PATH, PROMPT_PATH, OUTPUT_DIR, PAGINAS, 
    PAGES_PER_BLOCK, ALL_PAGES, TEMPERATURE, GEMINI_MODEL,
    OUTPUT_FORMAT  # <--- Importamos la nueva propiedad
)
from core.prompt_reader import PromptReader
from core.ai_generator import AIGenerator
from core.file_writer import FileWriter
from core.logger_config import app_logger
import re
import os

class DocumentProcessor:
    def __init__(self, pdf_path=None, output_dir=None, temperature=None):
        # 1. Configuración Dinámica
        self.pdf_path = pdf_path if pdf_path else PDF_PATH
        self.output_dir = output_dir if output_dir else OUTPUT_DIR
        self.temperature = temperature if temperature is not None else TEMPERATURE
        self.output_format = OUTPUT_FORMAT.lower()

        prompt_filename = f"prompt_{self.output_format}" 
        specific_prompt_path = os.path.join(os.path.dirname(PROMPT_PATH), prompt_filename)

        # 2. Inicialización de componentes
        self.prompt_reader = PromptReader(specific_prompt_path)
        self.ai_generator = AIGenerator(
            pages_per_block=PAGES_PER_BLOCK, 
            temperature=self.temperature
        )
        self.file_writer = FileWriter(self.output_dir)
        self.logger = app_logger
    
    def _clean_ai_response(self, text: str) -> str:
        """Limpieza inteligente según el formato de salida"""
        # 1. Eliminar bloques de código Markdown (común en ambos formatos)
        text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```xml\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```\s*', '', text)

        # 2. Limpieza específica para XML
        if self.output_format == "xml":
            text = re.sub(r'<\?xml.*?\?>', '', text, flags=re.DOTALL)
            text = re.sub(r'<documento[^>]*>', '', text, flags=re.DOTALL)
            text = text.replace('</documento>', '')
        
        # 3. Limpieza específica para JSON
        # (El FileWriter se encargará de validar si es un JSON parseable)
        
        return text.strip()

    def _pretty_print(self):
        if ALL_PAGES:
            paginas_info = "todas las páginas"
        else:
            paginas_info = f"páginas {PAGINAS[0]}-{PAGINAS[1]}"

        self.logger.info("-" * 45)
        self.logger.info(f"🚀 INICIANDO PROCESAMIENTO TFM")
        self.logger.info(f"📄 Archivo:    {os.path.basename(self.pdf_path)}")
        self.logger.info(f"🛠️  Formato:    {self.output_format.upper()}")
        self.logger.info(f"🌡️  Temp:       {self.temperature}")
        self.logger.info(f"📖 Rango:      {paginas_info}")
        self.logger.info(f"📂 Salida:     {self.output_dir}")
        self.logger.info("-" * 45)

    def process(self):
        """Método principal unificado"""
        try:
            self._pretty_print()
            
            # VALIDACIÓN
            if not os.path.exists(self.pdf_path):
                raise FileNotFoundError(f"El archivo PDF no existe: {self.pdf_path}")

            # PASO 1: Leer Prompt
            self.logger.info("📜 Cargando instrucciones del prompt...")
            prompt = self.prompt_reader.read()

            # PASO 2: Generar con IA
            self.logger.info(f"🤖 Solicitando generación a Gemini ({GEMINI_MODEL})...")
            response = self.ai_generator.generate_from_pdf(self.pdf_path, prompt)
            
            # PASO 3: Limpiar respuesta
            self.logger.info("🧹 Saneando respuesta (eliminando artefactos)...")
            response = self._clean_ai_response(response)

            # PASO 4: Guardar Resultados
            if response:
                # El FileWriter detectará internamente si debe envolverlo en XML o JSON
                saved_path = self.file_writer.save_with_counter(response, self.pdf_path)
                self.logger.info(f"💾 Proceso finalizado. Archivo creado en: {saved_path}")
            else:
                self.logger.warning("⚠️ La IA devolvió una respuesta vacía.")

        except Exception as e:
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str:
                self.logger.info("⏹️  PROCESO DETENIDO: Límite de cuota API alcanzado (RPD).")
                return 
            else:
                self.logger.error(f"❌ ERROR CRÍTICO: {error_str}")
                # En desarrollo/TFM es mejor lanzar el error para ver el traceback
                raise e 

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.process()