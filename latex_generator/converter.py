# latex_generator/converter.py

import os
import re
from lxml import etree
from pylatex import Document, Section, Subsection, Command, NoEscape
from pylatex.utils import italic

class XMLToLaTeXConverter:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        # Configuramos el documento con márgenes estándar para evitar Overfull hbox
        self.doc = Document(default_filepath='output_document', geometry_options={"margin": "2.5cm"})
        
        # Paquetes necesarios
        self.doc.packages.append(Command('usepackage', 'expex'))
        self.doc.packages.append(Command('usepackage[T1]', 'fontenc'))
        self.doc.packages.append(Command('usepackage[utf8]', 'inputenc'))

    def parse_and_generate(self):
        if not os.path.exists(self.xml_path):
            print(f"Error: No se encuentra {self.xml_path}")
            return

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(self.xml_path, parser)
        root = tree.getroot()

        # Limpiamos el nombre de la fuente para el título
        fuente = root.get('fuente', 'Documento').replace('_', ' ').replace('-', '--')
        self.doc.preamble.append(Command('title', f"Análisis Lingüístico: {fuente}"))
        self.doc.preamble.append(Command('author', 'Generado por Maya API TFM'))
        self.doc.append(NoEscape(r'\maketitle'))

        for pagina in root.xpath('//pagina'):
            num_pag = pagina.get('num')
            with self.doc.create(Section(f"Página {num_pag}")):
                self._process_elements(pagina)

    def _process_elements(self, container):
        for elemento in container:
            if elemento.tag == 'seccion':
                titulo = elemento.get('type', 'Sección')
                self.doc.append(Subsection(titulo))
                self._process_elements(elemento)
            
            elif elemento.tag == 'linea':
                texto = elemento.text.strip() if elemento.text else ""
                if texto:
                    # En lugar de \newline, usamos texto normal. 
                    # LaTeX se encarga de ajustar los párrafos.
                    self.doc.append(texto + " ") 
            
            elif elemento.tag == 'interlinear_gloss':
                # Añadimos un salto de párrafo antes de la glosa para que no se pegue al texto
                self.doc.append(NoEscape(r'\par\medskip'))
                self._process_gloss(elemento)
                self.doc.append(NoEscape(r'\medskip'))

    def _process_gloss(self, gloss):
        # 1. Extraer Frase y Traducción
        orig_node = gloss.find('.//original')
        trans_node = gloss.find('.//translation')
        original = orig_node.text.strip() if orig_node is not None else ""
        translation = trans_node.text.strip() if trans_node is not None else ""
        
        # 2. Análisis Morfológico (Líneas B y C)
        units_m = gloss.xpath('.//morpheme_analysis/unit')
        forms_m = " ".join([f"\\textbf{{{u.find('form').text.strip()}}}" for u in units_m if u.find('form') is not None])
        glosses_m = " ".join([u.find('gloss').text.strip() for u in units_m if u.find('gloss') is not None])

        # 3. Análisis Sintáctico (Lo preparamos para ir dentro de la glosa)
        syntax_node = gloss.find('.//syntactic_analysis')
        syntax_content = ""
        if syntax_node is not None:
            units_s = syntax_node.xpath('./unit')
            parts = []
            for u in units_s:
                f = u.find('form').text.strip() if u.find('form') is not None else ""
                g = u.find('gloss').text.strip() if u.find('gloss') is not None else ""
                if f or g:
                    parts.append(f"{f} [\\textsc{{{g}}}]")
            syntax_content = " ".join(parts)

        # 4. Construcción del bloque expex (Sin usar \gld para evitar errores)
        # Ponemos el análisis sintáctico como una línea destacada antes de la traducción
        expex_block = [
            r'\ex',
            r'\begingl',
            f'\\gla {original} //',   # Frase original
            f'\\glb {forms_m} //',    # Morfemas
            f'\\glc {glosses_m} //',   # Glosas morfológicas
        ]
        
        # Si hay sintaxis, la metemos con un formato especial
        syntax_line = f"\\glft \\textbf{{Sintaxis:}} {syntax_content} \\\\ " if syntax_content else "\\glft "
        
        expex_block.append(f"{syntax_line}`\\textit{{{translation}}}' //")
        expex_block.append(r'\endgl')
        expex_block.append(r'\xe')
        
        self.doc.append(NoEscape("\n".join(expex_block) + "\n"))

    def save_tex(self, filename):
        self.doc.generate_tex(filename)