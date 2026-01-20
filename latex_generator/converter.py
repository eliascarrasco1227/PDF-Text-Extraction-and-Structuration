# latex_generator/converter.py

import os
from lxml import etree
from pylatex import Document, Section, Subsection, Command, NoEscape
from pylatex.utils import italic, bold

class XMLToLaTeXConverter:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.doc = Document(default_filepath='output_document')
        self.doc.packages.append(Command('usepackage', 'expex'))
        self.doc.packages.append(Command('usepackage[utf8]', 'inputenc'))

    def parse_and_generate(self):
        if not os.path.exists(self.xml_path):
            print(f"Error: No se encuentra {self.xml_path}")
            return

        parser = etree.XMLParser(remove_blank_text=True) # Limpia espacios innecesarios
        tree = etree.parse(self.xml_path, parser)
        root = tree.getroot()

        self.doc.preamble.append(Command('title', f"Análisis Lingüístico: {root.get('fuente', 'Documento')}"))
        self.doc.preamble.append(Command('author', 'Generado por Maya API TFM'))
        self.doc.append(NoEscape(r'\maketitle'))

        for pagina in root.xpath('//pagina'):
            num_pag = pagina.get('num')
            with self.doc.create(Section(f"Página {num_pag}")):
                # Llamamos a un procesador recursivo para manejar el anidamiento
                self._process_elements(pagina)

    def _process_elements(self, container):
        """Procesa los elementos de forma recursiva respetando la jerarquía"""
        for elemento in container:
            if elemento.tag == 'seccion':
                # Usamos el atributo 'type' para el título, no el texto interior
                titulo = elemento.get('type', 'Sección')
                self.doc.append(Subsection(titulo))
                # IMPORTANTE: Procesamos lo que hay DENTRO de la sección
                self._process_elements(elemento)
            
            elif elemento.tag == 'linea':
                texto = elemento.text.strip() if elemento.text else ""
                if texto:
                    self.doc.append(texto + "\n")
            
            elif elemento.tag == 'interlinear_gloss':
                self._process_gloss(elemento)

    def _process_gloss(self, gloss):
        # Usamos find() con comprobación de seguridad para evitar errores de None
        orig_node = gloss.find('.//original')
        trans_node = gloss.find('.//translation')
        
        original = orig_node.text.strip() if orig_node is not None else ""
        translation = trans_node.text.strip() if trans_node is not None else ""
        
        # Extraemos morfemas
        units = gloss.xpath('.//morpheme_analysis/unit')
        
        forms_list = []
        glosses_list = []
        
        for u in units:
            f = u.find('form').text.strip() if u.find('form') is not None else "-"
            g = u.find('gloss').text.strip() if u.find('gloss') is not None else "-"
            # El tutor pidió: morfema en negrita (\textbf{})
            forms_list.append(f"\\textbf{{{f}}}")
            glosses_list.append(g)

        forms = " ".join(forms_list)
        glosses = " ".join(glosses_list)

        # Construcción del bloque expex
        expex_block = [
            r'\ex',
            r'\begingl',
            f'\\gla {original} //',
            f'\\glb {forms} //',
            f'\\glc {glosses} //',
            f"\\glft `{italic(translation)}' //",
            r'\endgl',
            r'\xe'
        ]
        
        self.doc.append(NoEscape("\n".join(expex_block) + "\n"))

    def save_tex(self, filename):
        self.doc.generate_tex(filename)