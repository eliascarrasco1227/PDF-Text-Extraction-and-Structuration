from config.properties import PDF_PATH, PROMPT_PATH, OUTPUT_DIR, PAGINAS, PAGES_PER_BLOCK, ALL_PAGES, TEMPERATURE
from core.prompt_reader import PromptReader
from core.ai_generator import AIGenerator
from core.file_writer import FileWriter
from core.logger_config import app_logger
import re
import os

class DocumentProcessor:
    def __init__(self, pdf_path=None, output_dir=None, temperature=None):
        # 1. Configuración Dinámica (Prioridad a argumentos, fallback a properties.py)
        self.pdf_path = pdf_path if pdf_path else PDF_PATH
        self.output_dir = output_dir if output_dir else OUTPUT_DIR
        # Si temperature es None, usamos el de properties, si no, el argumento
        self.temperature = temperature if temperature is not None else TEMPERATURE

        # 2. Inicialización de componentes
        self.prompt_reader = PromptReader(PROMPT_PATH)
        
        # Inyectamos la temperatura al generador
        self.ai_generator = AIGenerator(
            pages_per_block=PAGES_PER_BLOCK, 
            temperature=self.temperature
        )
        
        # Inyectamos el directorio de salida al escritor
        self.file_writer = FileWriter(self.output_dir)
        self.logger = app_logger
    
    def _clean_ai_response(self, text: str) -> str:
        """Limpieza de etiquetas extra que a veces pone Gemini"""
        # 1. Eliminar declaración XML
        text = re.sub(r'<\?xml.*?\?>', '', text, flags=re.DOTALL)
        # 2. Eliminar etiqueta <documento>
        text = re.sub(r'<documento[^>]*>', '', text, flags=re.DOTALL)
        text = text.replace('</documento>', '')
        # 3. Eliminar markdown
        text = re.sub(r'```xml', '', text, flags=re.IGNORECASE)
        text = text.replace('```', '')
        return text.strip()

    def _pretty_print(self):
        # Lógica para mostrar info bonita en el log
        if ALL_PAGES:
            paginas_info = "todas las páginas"
        else:
            paginas_info = f"páginas {PAGINAS[0]}-{PAGINAS[1]}"

        self.logger.info("-" * 40)
        self.logger.info(f"📄 Procesando: {os.path.basename(self.pdf_path)}")
        self.logger.info(f"🌡️  Temp:      {self.temperature}")
        self.logger.info(f"📂 Salida:    {self.output_dir}")
        self.logger.info(f"📖 Rango:     {paginas_info}")
        self.logger.info("-" * 40)

    def process(self):
        """
        Método principal unificado.
        """
        try:
            self._pretty_print()
            
            # VALIDACIÓN
            if not os.path.exists(self.pdf_path):
                raise FileNotFoundError(f"El archivo PDF no existe: {self.pdf_path}")

            # PASO 1: Leer Prompt
            self.logger.info("📜 Leyendo prompt...")
            prompt = self.prompt_reader.read()

            # PASO 2: Generar con IA
            self.logger.info(f"🤖 Iniciando generación con Temperatura {self.temperature}...")
            response = self.ai_generator.generate_from_pdf(self.pdf_path, prompt)
            
            # PASO 3: Limpiar respuesta
            self.logger.info("🧹 Limpiando respuesta de la IA...")
            response = self._clean_ai_response(response)

            # PASO 4: Guardar Resultados
            if response:
                saved_path = self.file_writer.save_with_counter(response)
                self.logger.info(f"✅ Guardado correctamente en: {saved_path}")
            else:
                self.logger.warning("⚠️ La respuesta de la IA estaba vacía.")

        except Exception as e:
            self.logger.error(f"❌ Error durante el proceso: {str(e)}")
            raise e 

if __name__ == "__main__":
    # Ejecución manual (usa defaults de properties.py)
    processor = DocumentProcessor()
    processor.process()