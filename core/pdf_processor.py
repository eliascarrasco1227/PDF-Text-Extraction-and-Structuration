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
                total_pages = len(pdf.pages)
                # Ajuste correcto: ambos valores base 1, convertir a base 0
                start = max(0, page_range[0] - 1)
                end = min(total_pages, page_range[1])  # end base 1

                # Para incluir la página final, sumamos 1 a end (porque range no incluye el último)
                end = min(total_pages, end)  # end no puede ser mayor que total_pages
                if start > end - 1:
                    self.logger.warning(f"Rango inválido ajustado a: ({start + 1}, {end})")
                    start = end - 1  # ajusta para evitar error

                writer = PdfWriter()
                for i in range(start, end):
                    writer.add_page(pdf.pages[i])
                
                output = io.BytesIO()
                writer.write(output)
                
                self.logger.debug(f"Extraídas {end - start} páginas exitosamente")
                return output.getvalue()
                
        except Exception as e:
            self.logger.error(f"Error extrayendo páginas: {e}", exc_info=True)
            raise