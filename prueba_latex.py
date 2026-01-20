# test_latex.py
# pip install pylatex

from latex_generator.converter import XMLToLaTeXConverter

# Suponiendo que tienes un XML generado en tu carpeta test_set o output
xml_input = "test_set/Gramatica-Normativa-Kaqchikel_páginas_172.xml"

print("🚀 Iniciando conversión XML a LaTeX...")
converter = XMLToLaTeXConverter(xml_input)
converter.parse_and_generate()

# Generamos el .tex para que puedas revisarlo
converter.save_tex("analisis_maya")
print("✅ Archivo .tex generado: analisis_maya.tex")

# Si tienes pdflatex instalado, puedes descomentar la siguiente línea:
# converter.save_pdf("analisis_maya")