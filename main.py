from config.properties import PDF_PATH, PROMPT_PATH, OUTPUT_DIR, PAGINAS, PAGES_PER_BLOCK, ALL_PAGES
from core.prompt_reader import PromptReader
from core.ai_generator import AIGenerator
from core.file_writer import FileWriter
from core.logger_config import app_logger
import re

class DocumentProcessor:
    def __init__(self):
        self.prompt_reader = PromptReader(PROMPT_PATH)
        self.ai_generator = AIGenerator(pages_per_block=PAGES_PER_BLOCK)
        self.file_writer = FileWriter(OUTPUT_DIR)
        self.logger = app_logger

    def _pretty_print(self):
        if ALL_PAGES:
            paginas_info = "todas las páginas"
        else:
            paginas_info = f"páginas {PAGINAS[0]}-{PAGINAS[1]}"

        CHAIN_SIZE = 38
        PROGRAM_NAME = "PDF TEXT EXTRACTOR AND STRUCTURATOR"

        self.logger.info("-" * CHAIN_SIZE)
        self.logger.info(f"| {PROGRAM_NAME} |")
        self.logger.info("-" * CHAIN_SIZE)
        self.logger.info("")

        self.logger.info(f"📄 Procesando: {PDF_PATH}")
        self.logger.info(f"📖 Páginas a procesar: {paginas_info}")
        self.logger.info(f"📦 Bloques de: {PAGES_PER_BLOCK} páginas")
        self.logger.info(f"📝 Prompt usado: {PROMPT_PATH}")
        self.logger.info("-" * CHAIN_SIZE)
        self.logger.info("")
    
    def _clean_ai_response(self, text: str) -> str:
        """
        Limpia las etiquetas XML de documento y cabeceras que la IA pueda haber generado
        para evitar duplicados con el FileWriter.
        """
        # 1. Eliminar declaración XML (<?xml ... ?>)
        text = re.sub(r'<\?xml.*?\?>', '', text, flags=re.DOTALL)
        
        # 2. Eliminar etiqueta de apertura <documento ...> (con cualquier atributo)
        text = re.sub(r'<documento[^>]*>', '', text, flags=re.DOTALL)
        
        # 3. Eliminar etiqueta de cierre </documento>
        text = text.replace('</documento>', '')
        
        # 4. Eliminar bloques de código markdown si la IA los pone (```xml ... ```)
        text = re.sub(r'```xml', '', text, flags=re.IGNORECASE)
        text = text.replace('```', '')
        
        return text.strip()

    def run(self):
        try:
            self._pretty_print()
            
            # 1. Leer prompt
            prompt = self.prompt_reader.read()

            # 2. Generar respuesta
            self.logger.info("🤖 Generando respuesta")
            response = self.ai_generator.generate_from_pdf(PDF_PATH, prompt)

            # --- CORRECCIÓN APLICADA AQUÍ ---
            # 3. Limpiar respuesta antes de procesar
            self.logger.info("🧹 Limpiando respuesta de la IA...")
            response = self._clean_ai_response(response)
            # --------------------------------

            # 4. Analizar respuesta (búsqueda de páginas)
            page_numbers = re.findall(r'<pagina num="(\d+)">', response)
            self.logger.info(f"📊 Páginas procesadas encontradas: {sorted(set(map(int, page_numbers)))}")

            self.logger.info("\n🤖 Fragmento de respuesta:")
            self.logger.info(response[:200] + "...")
            
            # 5. Guardar respuesta (El FileWriter añadirá las etiquetas correctas)
            saved_path = self.file_writer.save_with_counter(response)
            self.logger.info(f"\n💾 XML guardado en: {saved_path}")

        except Exception as e:
            if "503" in str(e):
                self.logger.error("❌ El servidor de Gemini está sobrecargado. Por favor, intenta nuevamente más tarde.")
            else:
                self.logger.error(f"❌ Error durante el procesamiento: {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.run()