# core/file_writer.py
import os
from config.properties import PAGINAS, ALL_PAGES
from PyPDF2 import PdfReader
from core.logger_config import app_logger

class FileWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = app_logger
    
    def _get_total_pages(self, pdf_path: str) -> int:
        """Obtiene el número total de páginas del PDF dinámicamente"""
        try:
            with open(pdf_path, 'rb') as f:
                pdf = PdfReader(f)
                return len(pdf.pages)
        except Exception as e:
            self.logger.error(f"Error al obtener total de páginas de {pdf_path}: {str(e)}")
            return 0
    
    def _generate_xml_wrapper(self, content: str, pdf_path: str) -> str:
        """Genera el envoltorio XML con metadatos basados en el PDF procesado"""
        try:
            # Usamos el nombre del PDF actual, NO el global
            pdf_name = os.path.basename(pdf_path)
            
            if ALL_PAGES:
                total_pages = self._get_total_pages(pdf_path)
                paginas_str = f"1-{total_pages}"
            else:
                paginas_str = f"{PAGINAS[0]}-{PAGINAS[1]}"
                
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<documento fuente="{pdf_name}" paginas="{paginas_str}">
{content}
</documento>'''
        except Exception as e:
            self.logger.warning(f"No se pudo generar wrapper completo: {str(e)}")
            return f"<documento>{content}</documento>"

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.output_dir, filename)

    def save_with_counter(self, content: str, original_pdf_path: str) -> str:
        """
        Guarda el contenido.
        :param content: Texto a guardar
        :param original_pdf_path: Ruta del PDF que originó este contenido (para el nombre)
        """
        try:
            # Extraemos el nombre del archivo real que se está procesando
            input_file_name = os.path.splitext(os.path.basename(original_pdf_path))[0]
            
            if ALL_PAGES:
                total_pages = self._get_total_pages(original_pdf_path)
                pages_range = f"páginas_1-{total_pages}"
            else:
                pages_range = f"páginas_{PAGINAS[0]}-{PAGINAS[1]}"
            
            # Construimos el nombre de salida basado en el input real
            output_file_base = f"{input_file_name}_{pages_range}"
            
            xml_content = self._generate_xml_wrapper(content, original_pdf_path)
            counter = 1
            
            # Buscamos siguiente versión disponible
            while os.path.exists(self._get_path(f"{output_file_base}_version_{counter}.xml")):
                counter += 1
            
            final_name = f"{output_file_base}_version_{counter}.xml"
            final_path = self._save_file(xml_content, final_name)
            
            self.logger.info(f"Archivo guardado como: {final_name}")
            return final_path
            
        except Exception as e:
            self.logger.error(f"Error al guardar archivo: {str(e)}")
            raise
    
    def _save_file(self, content: str, filename: str) -> str:
        """Guarda el contenido en disco"""
        try:
            path = self._get_path(filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.debug(f"Contenido escrito en: {path}")
            return path
        except Exception as e:
            self.logger.error(f"No se pudo escribir en disco: {str(e)}")
            raise