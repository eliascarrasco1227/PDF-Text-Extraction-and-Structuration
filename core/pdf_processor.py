# pdf_processor.py
from PyPDF2 import PdfReader, PdfWriter
import io
from core.logger_config import app_logger

class PDFProcessor:
    def __init__(self):
        self.logger = app_logger

    def extract_pages(self, pdf_path: str, page_range: tuple) -> bytes:
        """Extrae un rango de páginas (inclusive) y devuelve PDF en bytes"""
        try:
            self.logger.debug(f"Extrayendo páginas {page_range} de {pdf_path}")
            
            with open(pdf_path, 'rb') as f:
                pdf = PdfReader(f)
                start = max(0, page_range[0] - 1)
                end = min(len(pdf.pages), page_range[1])

                if start >= end:
                    start = end - 1
                    self.logger.warning(f"Rango inválido ajustado a: ({start + 1}, {end})")
                
                writer = PdfWriter()
                for i in range(start, end):
                    writer.add_page(pdf.pages[i])
                
                output = io.BytesIO()
                writer.write(output)
                
                self.logger.debug(f"Extraídas {end - start} páginas exitosamente")
                return output.getvalue()
                
        except Exception as e:
            self.logger.error(f"Error al extraer páginas: {str(e)}", exc_info=True)
            raise