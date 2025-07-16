from PyPDF2 import PdfReader, PdfWriter
import io

class PDFProcessor:
    @staticmethod
    def extract_pages(pdf_path: str, page_range: tuple) -> bytes:
        """Extrae un rango de páginas y devuelve PDF en bytes"""
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            start = max(0, page_range[0] - 1)  # Convertir a base 0
            end = min(len(pdf.pages), page_range[1])
            
            writer = PdfWriter()
            for i in range(start, end):
                writer.add_page(pdf.pages[i])
            
            output = io.BytesIO()
            writer.write(output)
            return output.getvalue()