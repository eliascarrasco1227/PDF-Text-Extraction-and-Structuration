# pdf_generator/compiler.py

import subprocess
import os
import logging
from core.logger_config import app_logger

class LaTeXCompiler:
    """
    Módulo encargado de compilar archivos .tex para generar PDFs.
    Requiere que pdflatex (MiKTeX o TeX Live) esté instalado en el sistema.
    """

    def __init__(self):
        self.logger = app_logger

    def compile_to_pdf(self, tex_path, output_dir=None):
        """
        Compila un archivo .tex usando pdflatex.
        :param tex_path: Ruta al archivo .tex
        :param output_dir: Carpeta donde se guardará el PDF (por defecto la misma del .tex)
        """
        if not os.path.exists(tex_path):
            self.logger.error(f"❌ No se encontró el archivo LaTeX: {tex_path}")
            return False

        # Si no se especifica output_dir, usamos la carpeta del archivo .tex
        if output_dir is None:
            output_dir = os.path.dirname(tex_path)

        # Comando para compilar
        # -interaction=nonstopmode: Para que no se detenga si hay errores menores
        # -output-directory: Dónde soltar el PDF y archivos temporales
        command = [
            "pdflatex",
            "-interaction=nonstopmode",
            f"-output-directory={output_dir}",
            tex_path
        ]

        try:
            self.logger.info(f"⏳ Compilando {tex_path} a PDF...")
            
            # Ejecutamos el comando del sistema
            result = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                check=True
            )
            
            self.logger.info(f"✅ PDF generado con éxito en: {output_dir}")
            
            # Opcional: Limpiar archivos basura (.aux, .log) que genera LaTeX
            self._clean_temp_files(tex_path, output_dir)
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Error crítico de LaTeX: {e.stdout}")
            return False
        except FileNotFoundError:
            self.logger.error("❌ No se encontró 'pdflatex'. Asegúrate de tener MiKTeX o TeX Live instalado y en el PATH.")
            return False

    def _clean_temp_files(self, tex_path, output_dir):
        """Borra los archivos auxiliares (.aux, .log, .out) para mantener limpia la carpeta"""
        base_name = os.path.splitext(os.path.basename(tex_path))[0]
        extensions = [".aux", ".log", ".out", ".toc"]
        
        for ext in extensions:
            temp_file = os.path.join(output_dir, base_name + ext)
            if os.path.exists(temp_file):
                os.remove(temp_file)