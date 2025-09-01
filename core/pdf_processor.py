# Updated pdf_processor.py
from PyPDF2 import PdfReader, PdfWriter
import io

class PDFProcessor:
    @staticmethod
    def extract_pages(pdf_path: str, page_range: tuple) -> bytes:
        """Extrae un rango de páginas (inclusive) y devuelve PDF en bytes"""
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            # Convertir a base 0 y hacer el rango inclusivo
            start = max(0, page_range[0] - 1)  # Página inicial en base 0
            end = min(len(pdf.pages), page_range[1])  # Página final en base 1

            # Handle case where start > end (invalid range)
            if start >= end:
                    start = end - 1  # Ensure at least one page
            
            # Para range() necesitamos end + 1 porque es exclusivo
            writer = PdfWriter()
            for i in range(start, end):  # end es exclusivo, así que esto es correcto
                writer.add_page(pdf.pages[i])
            
            output = io.BytesIO()
            writer.write(output)
            return output.getvalue()