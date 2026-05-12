from config.properties import PDF_PATH, PROMPT_PATH, OUTPUT_DIR, PAGINAS, PAGES_PER_BLOCK, ALL_PAGES, TEMPERATURE
from core.prompt_reader import PromptReader
from core.ai_generator import AIGenerator
from core.file_writer import FileWriter
from core.logger_config import app_logger
from latex_generator.converter import XMLToLaTeXConverter 
from pdf_generator.compiler import LaTeXCompiler
import re
import os

class DocumentProcessor:
    def __init__(self, pdf_path=None, output_dir=None, temperature=None):
        # 1. Configuración Dinámica
        self.pdf_path = pdf_path if pdf_path else PDF_PATH
        self.output_dir = output_dir if output_dir else OUTPUT_DIR
        self.temperature = temperature if temperature is not None else TEMPERATURE

        # 2. Inicialización de componentes
        self.prompt_reader = PromptReader(PROMPT_PATH)
        self.ai_generator = AIGenerator(
            pages_per_block=PAGES_PER_BLOCK, 
            temperature=self.temperature
        )
        self.file_writer = FileWriter(self.output_dir)
        self.logger = app_logger
    
    def _clean_ai_response(self, text: str) -> str:
        """Limpieza robusta de etiquetas y markdown"""
        # (Se mantiene igual que tu código original)
        text = re.sub(r'<\?xml.*?\?>', '', text, flags=re.DOTALL)
        text = re.sub(r'<documento[^>]*>', '', text, flags=re.DOTALL)
        text = text.replace('</documento>', '')
        text = re.sub(r'```\w*', '', text) 
        text = text.replace('```', '')
        return text.strip()

    def _pretty_print(self):
        # (Se mantiene igual que tu código original)
        if ALL_PAGES:
            paginas_info = "todas las páginas"
        else:
            paginas_info = f"páginas {PAGINAS[0]}-{PAGINAS[1]}"

        self.logger.info("-" * 40)
        self.logger.info(f"📄 Procesando: {os.path.basename(self.pdf_path)}")
        self.logger.info(f"🌡️ Temp:      {self.temperature}")
        self.logger.info(f"📂 Salida:    {self.output_dir}")
        self.logger.info(f"📖 Rango:     {paginas_info}")
        self.logger.info("-" * 40)

    def process(self):
        """Método principal unificado"""
        try:
            self._pretty_print()
            
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

            # PASO 4: Guardar XML y Generar LaTeX
            if response:
                # Guardamos el XML
                saved_xml_path = self.file_writer.save_with_counter(response, self.pdf_path)
                self.logger.info(f"✅ XML guardado correctamente en: {saved_xml_path}")

                # --- NUEVA ETAPA: GENERACIÓN DE LATEX ---
                try:
                    self.logger.info("🎨 Generando archivo LaTeX a partir del XML...")
                    # Quitamos la extensión .xml para el nombre del archivo .tex
                    base_name = os.path.splitext(saved_xml_path)[0]
                    
                    converter = XMLToLaTeXConverter(saved_xml_path)
                    converter.parse_and_generate()
                    converter.save_tex(base_name) # Guardará un archivo .tex con el mismo nombre

                    # 2. Compilar a PDF (NUEVO PASO)
                    compiler = LaTeXCompiler()
                    success = compiler.compile_to_pdf(base_name + ".tex")
                    
                    self.logger.info(f"✨ LaTeX generado correctamente en: {base_name}.tex")

                    return saved_xml_path
                
                except Exception as e:
                    self.logger.error(f"❌ Error durante la generación de LaTeX: {str(e)}")
                # ----------------------------------------

            else:
                self.logger.warning("⚠️ La respuesta de la IA estaba vacía.")

        except Exception as e:
            # (Se mantiene igual que tu gestión de errores original)
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str:
                self.logger.info("⏹️  Proceso detenido por límite de API.")
                return 
            else:
                self.logger.error(f"❌ Error durante el proceso: {error_str}")
                raise e 

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.process()