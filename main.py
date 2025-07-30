from config.paths import PDF_PATH, PROMPT_PATH, OUTPUT_DIR, PAGINAS
from core.prompt_reader import PromptReader
from core.ai_generator import AIGenerator
from core.file_writer import FileWriter

class DocumentProcessor:
    def __init__(self):
        self.prompt_reader = PromptReader(PROMPT_PATH)
        self.ai_generator = AIGenerator()
        self.file_writer = FileWriter(OUTPUT_DIR)
    
    def run(self):
        print(f"📄 Procesando {PDF_PATH} (páginas {PAGINAS[0]}-{PAGINAS[1]})")
        
        # 1. Leer prompt
        prompt = self.prompt_reader.read()
        print(f"📝 Prompt usado: {self.prompt_reader.preview}")

        # 2. Generar respuesta
        print("🤖 Generando respuesta...")
        response = self.ai_generator.generate_from_pdf(PDF_PATH, prompt)

        print("\n🤖 Fragmento de respuesta:")
        print(response[:200] + "...")
        
        saved_path = self.file_writer.save_with_counter(response)
        print(f"\n💾 XML guardado en: {saved_path}")

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.run()

    