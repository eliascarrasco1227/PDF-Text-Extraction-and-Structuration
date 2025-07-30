import os
from datetime import datetime
from config.paths import PDF_PATH, PAGINAS

class FileWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _generate_xml_wrapper(self, content: str) -> str:
        """Genera el envoltorio XML con metadatos"""
        pdf_name = os.path.basename(PDF_PATH)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<documento fuente="{pdf_name}" paginas="{PAGINAS[0]}-{PAGINAS[1]}">
{content}
</documento>'''
    
    def save_with_counter(self, content: str) -> str:
        """Guarda con numeración y formato XML"""
        xml_content = self._generate_xml_wrapper(content)
        counter = 1
        while os.path.exists(self._get_path(f"respuesta_{counter}.xml")):
            counter += 1
        return self._save_file(xml_content, f"respuesta_{counter}.xml")
    
    def _save_file(self, content: str, filename: str) -> str:
        path = self._get_path(filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def _get_path(self, filename: str) -> str:
        return os.path.join(self.output_dir, filename)