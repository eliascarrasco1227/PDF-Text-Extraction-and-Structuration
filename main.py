from config.paths import PDF_PATH, PROMPT_PATH, OUTPUT_DIR, PAGINAS, PAGES_PER_BLOCK, ALL_PAGES
from core.prompt_reader import PromptReader
from core.ai_generator import AIGenerator
from core.file_writer import FileWriter
import re

class DocumentProcessor:
    def __init__(self):
        self.prompt_reader = PromptReader(PROMPT_PATH)
        self.ai_generator = AIGenerator(pages_per_block=PAGES_PER_BLOCK)
        self.file_writer = FileWriter(OUTPUT_DIR)

    def _pretty_print(self):
        if ALL_PAGES:
            paginas_info = "todas las páginas"
        else:
            paginas_info = f"páginas {PAGINAS[0]}-{PAGINAS[1]}"

        CHAIN_SIZE = 38
        PROGRAM_NAME = "PDF TEXT EXTRACTOR AND STRUCTURATOR"

        print("-" * CHAIN_SIZE)
        print(f"| {PROGRAM_NAME} |")
        print("-" * CHAIN_SIZE)
        print("")

        print(f"📄 Procesando: {PDF_PATH}")
        print(f"📖 Páginas a procesar: {paginas_info}")
        print(f"📦 Bloques de: {PAGES_PER_BLOCK} páginas")
        print(f"📝 Prompt usado: {PROMPT_PATH}")
        print("-" * CHAIN_SIZE)
        print("")
    
    def run(self):
        self._pretty_print()
        
        # 1. Leer prompt
        prompt = self.prompt_reader.read()

        # 2. Generar respuesta
        print("🤖 Generando respuesta")
        response = self.ai_generator.generate_from_pdf(PDF_PATH, prompt)

        page_numbers = re.findall(r'<pagina num="(\d+)">', response)
        print(f"📊 Páginas procesadas encontradas: {sorted(set(map(int, page_numbers)))}")

        print("\n🤖 Fragmento de respuesta:")
        print(response[:200] + "...")
        
        saved_path = self.file_writer.save_with_counter(response)
        print(f"\n💾 XML guardado en: {saved_path}")

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.run()