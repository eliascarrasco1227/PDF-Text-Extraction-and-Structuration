from config.paths import PDF_PATH, PROMPT_PATH, OUTPUT_DIR
from core.prompt_reader import PromptReader
from core.ai_generator import AIGenerator
from core.file_writer import FileWriter

class DocumentProcessor:
    def __init__(self):
        self.prompt_reader = PromptReader(PROMPT_PATH)
        self.ai_generator = AIGenerator()
        self.file_writer = FileWriter(OUTPUT_DIR)
    
    def run(self):
        # 1. Leer prompt
        prompt = self.prompt_reader.read()
        print(f"📝 Prompt usado: {self.prompt_reader.preview}")
        
        # 2. Generar respuesta
        response = self.ai_generator.generate_from_pdf(PDF_PATH, prompt)
        print("\n🤖 Respuesta generada:")
        print(response[:200] + "...")  # Muestra fragmento
        
        # 3. Guardar (elige un método)
        saved_path = self.file_writer.save_with_counter(response)
        # saved_path = self.file_writer.save_with_timestamp(response)
        
        print(f"\n💾 Respuesta guardada en: {saved_path}")

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.run()