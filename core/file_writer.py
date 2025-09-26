# file_writer.py
import os
from datetime import datetime
from config.properties import PDF_PATH, PAGINAS, ALL_PAGES
from PyPDF2 import PdfReader
from core.logger_config import app_logger

class FileWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = app_logger
    
    def _get_total_pages(self) -> int:
        """Obtiene el número total de páginas del PDF"""
        try:
            with open(PDF_PATH, 'rb') as f:
                pdf = PdfReader(f)
                return len(pdf.pages)
        except Exception as e:
            self.logger.error(f"Error al obtener total de páginas: {str(e)}")
            raise
    
    def _generate_xml_wrapper(self, content: str) -> str:
        """Genera el envoltorio XML con metadatos"""
        try:
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
            
        except Exception as e:
            self.logger.error(f"Error al generar wrapper XML: {str(e)}")
            raise
    
    def save_with_counter(self, content: str) -> str:
        """Guarda con numeración y formato XML"""
        try:
            INPUT_FILE_NAME = PDF_PATH.split('/')[-1].replace('.pdf', '')
            
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
            
            final_path = self._save_file(xml_content, f"{OUTPUT_FILE_NAME}_version_{counter}.xml")
            self.logger.info(f"Archivo guardado como: {OUTPUT_FILE_NAME}_version_{counter}.xml")
            return final_path
            
        except Exception as e:
            self.logger.error(f"Error al guardar archivo: {str(e)}")
            raise
    
    def _save_file(self, content: str, filename: str) -> str:
        """Guarda el contenido en un archivo"""
        try:
            path = self._get_path(filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.debug(f"Contenido escrito en: {path}")
            return path
        except Exception as e:
            self.logger.error(f"Error al escribir archivo: {str(e)}")
            raise
    
    def _get_path(self, filename: str) -> str:
        return os.path.join(self.output_dir, filename)