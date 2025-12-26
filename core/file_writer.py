# core/file_writer.py
import os
import json
import time
from config.properties import PAGINAS, ALL_PAGES, OUTPUT_FORMAT
from PyPDF2 import PdfReader
from core.logger_config import app_logger

class FileWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = app_logger
        self.output_format = OUTPUT_FORMAT.lower()
    
    def _get_total_pages(self, pdf_path: str) -> int:
        """Obtiene el número total de páginas del PDF dinámicamente"""
        try:
            with open(pdf_path, 'rb') as f:
                pdf = PdfReader(f)
                return len(pdf.pages)
        except Exception as e:
            self.logger.error(f"Error al obtener total de páginas de {pdf_path}: {str(e)}")
            return 0
    
    def _get_metadata(self, pdf_path: str) -> dict:
        """Centraliza la generación de metadatos para ambos formatos"""
        pdf_name = os.path.basename(pdf_path)
        if ALL_PAGES:
            total_pages = self._get_total_pages(pdf_path)
            paginas_str = f"1-{total_pages}"
        else:
            paginas_str = f"{PAGINAS[0]}-{PAGINAS[1]}"
        
        return {
            "fuente": pdf_name,
            "paginas_procesadas": paginas_str,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "formato_salida": self.output_format.upper()
        }

    def _generate_xml_wrapper(self, content: str, pdf_path: str) -> str:
        """Envuelve el contenido en una estructura XML válida"""
        meta = self._get_metadata(pdf_path)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<documento fuente="{meta['fuente']}" paginas="{meta['paginas_procesadas']}" fecha="{meta['timestamp']}">
{content}
</documento>'''

    def _generate_json_wrapper(self, content: str, pdf_path: str) -> str:
        """
        Convierte el contenido string de la IA en un objeto JSON válido 
        combinado con metadatos.
        """
        meta = self._get_metadata(pdf_path)
        
        try:
            # Intentamos parsear el contenido para que no se guarde como un string escapado,
            # sino como un objeto JSON real anidado.
            # Si el contenido son varios bloques JSON seguidos (común en procesamiento por bloques),
            # intentamos sanearlo.
            if content.count('{') > 1 and not content.strip().startswith('['):
                # Es posible que Gemini haya devuelto múltiples objetos sueltos
                # Lo convertimos en una lista válida: [obj1, obj2...]
                sanitized_content = "[" + content.replace('}{', '},{') + "]"
                json_data = json.loads(sanitized_content)
            else:
                json_data = json.loads(content)
                
            full_structure = {
                "metadata": meta,
                "data": json_data
            }
            return json.dumps(full_structure, indent=4, ensure_ascii=False)
            
        except json.JSONDecodeError:
            self.logger.warning("⚠️ El contenido no es JSON válido. Guardando como texto plano dentro de JSON.")
            return json.dumps({"metadata": meta, "raw_content": content}, indent=4)

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.output_dir, filename)

    def save_with_counter(self, content: str, original_pdf_path: str) -> str:
        """
        Guarda el contenido en el formato configurado (XML o JSON).
        """
        try:
            input_file_name = os.path.splitext(os.path.basename(original_pdf_path))[0]
            
            # Determinamos el rango de páginas para el nombre del archivo
            if ALL_PAGES:
                total_pages = self._get_total_pages(original_pdf_path)
                pages_range = f"páginas_1-{total_pages}"
            else:
                pages_range = f"páginas_{PAGINAS[0]}-{PAGINAS[1]}"
            
            output_file_base = f"{input_file_name}_{pages_range}"
            extension = f".{self.output_format}"
            
            # Generar el contenido estructurado según formato
            if self.output_format == "json":
                final_content = self._generate_json_wrapper(content, original_pdf_path)
            else:
                final_content = self._generate_xml_wrapper(content, original_pdf_path)
            
            # Buscador de versiones (ahora dinámico con la extensión)
            counter = 1
            while os.path.exists(self._get_path(f"{output_file_base}_version_{counter}{extension}")):
                counter += 1
            
            final_name = f"{output_file_base}_version_{counter}{extension}"
            final_path = self._save_file(final_content, final_name)
            
            self.logger.info(f"✅ Resultado guardado en [{self.output_format.upper()}]: {final_name}")
            return final_path
            
        except Exception as e:
            self.logger.error(f"❌ Error al guardar archivo: {str(e)}")
            raise
    
    def _save_file(self, content: str, filename: str) -> str:
        """Guarda el contenido en disco"""
        try:
            path = self._get_path(filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return path
        except Exception as e:
            self.logger.error(f"No se pudo escribir en disco: {str(e)}")
            raise