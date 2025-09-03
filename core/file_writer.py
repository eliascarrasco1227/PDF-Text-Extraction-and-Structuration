import os
from datetime import datetime
from config.paths import PDF_PATH, PAGINAS, ALL_PAGES
from PyPDF2 import PdfReader

class FileWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _get_total_pages(self) -> int:
        """Obtiene el número total de páginas del PDF"""
        with open(PDF_PATH, 'rb') as f:
            pdf = PdfReader(f)
            return len(pdf.pages)
    
    def _generate_xml_wrapper(self, content: str) -> str:
        """Genera el envoltorio XML con metadatos"""
        pdf_name = os.path.basename(PDF_PATH)
        
        if ALL_PAGES:
            total_pages = self._get_total_pages()
            paginas_str = f"1-{total_pages}"
        else:
            paginas_str = f"{PAGINAS[0]}-{PAGINAS[1]}"
            
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<documento fuente="{pdf_name}" paginas="{paginas_str}">
{content}
</documento>'''
    
    def save_with_counter(self, content: str) -> str:
        """Guarda con numeración y formato XML"""
        INPUT_FILE_NAME = PDF_PATH.split('/')[-1].replace('.pdf', '')
        
        # Determinar el rango de páginas para el nombre del archivo
        if ALL_PAGES:
            total_pages = self._get_total_pages()
            pages_range = f"páginas_1-{total_pages}"
        else:
            pages_range = f"páginas_{PAGINAS[0]}-{PAGINAS[1]}"
        
        OUTPUT_FILE_NAME = f"{INPUT_FILE_NAME}_{pages_range}"
        
        xml_content = self._generate_xml_wrapper(content)
        counter = 1
        while os.path.exists(self._get_path(f"{OUTPUT_FILE_NAME}_version_{counter}.xml")):
            counter += 1
        return self._save_file(xml_content, f"{OUTPUT_FILE_NAME}_version_{counter}.xml")
    
    def _save_file(self, content: str, filename: str) -> str:
        path = self._get_path(filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def _get_path(self, filename: str) -> str:
        return os.path.join(self.output_dir, filename)