# latex_generator/converter.py

import os
import re
from lxml import etree
from pylatex import Document, Section, Subsection, Command, NoEscape
from pylatex.utils import italic

class XMLToLaTeXConverter:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.doc = Document(default_filepath='output_document', geometry_options={"margin": "2.5cm"})
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
        fuente = root.get('fuente', 'Documento').replace('_', ' ').replace('-', '--')
        self.doc.preamble.append(Command('title', f"Análisis Lingüístico: {fuente}"))
        self.doc.preamble.append(Command('author', 'Generado por el TFM de Elías Carrasco'))
        self.doc.append(NoEscape(r'\maketitle'))
        for pagina in root.xpath('//pagina'):
            num_pag = pagina.get('num')
            with self.doc.create(Section(f"Página {num_pag}")):
                self._process_elements(pagina)
    
    def _clean_for_latex(self, text: str) -> str:
        """Limpia caracteres Unicode problemáticos para pdflatex"""
        if not text:
            return ""
        
        # Mapa de caracteres extraños que hemos detectado en tus logs (U+06F0, etc)
        # Convertimos números árabes/índicos a números estándar
        replacements = {
            '\u06f0': '0', '\u06f1': '1', '\u06f2': '2', '\u06f3': '3', 
            '\u06f4': '4', '\u06f5': '5', '\u06f6': '6', '\u06f7': '7', 
            '\u06f8': '8', '\u06f9': '9',
            # Otros caracteres de control que suelen dar guerra
            '\u200b': '',  # Zero width space
            '\u200e': '',  # Left-to-right mark
            '\u200f': '',  # Right-to-left mark
        }
        
        for char, rep in replacements.items():
            text = text.replace(char, rep)
            
        # Escapamos caracteres especiales de LaTeX si no vienen ya protegidos
        # (Pero con cuidado de no romper las etiquetas \textbf o \textit)
        # Por ahora, nos centramos en los caracteres Unicode que fallaron.
        return text

    def _process_elements(self, container):
        for elemento in container:
            if elemento.tag == 'seccion':
                titulo = elemento.get('type', 'Seccion')
                self.doc.append(Subsection(self._clean_for_latex(titulo)))
                self._process_elements(elemento)
            elif elemento.tag == 'linea':
                texto = elemento.text.strip() if elemento.text else ""
                if texto: self.doc.append(self._clean_for_latex(texto) + " ") 
            elif elemento.tag == 'interlinear_gloss':
                self.doc.append(NoEscape(r'\par\medskip'))
                self._process_gloss(elemento)
                self.doc.append(NoEscape(r'\medskip'))

    def _process_gloss(self, gloss):
        orig_node = gloss.find('.//original')
        trans_node = gloss.find('.//translation')
        original = orig_node.text.strip() if orig_node is not None else ""
        translation = trans_node.text.strip() if trans_node is not None else ""
        
        # --- NUEVA LÓGICA DE AGRUPAMIENTO ---
        units_m = gloss.xpath('.//morpheme_analysis/unit')
        
        word_blocks_form = []
        word_blocks_gloss = []
        
        current_f_block = ""
        current_g_block = ""

        for i, u in enumerate(units_m):
            # Usamos (node.text or "") para convertir None en un string vacío antes de hacer strip()
            f_node = u.find('form')
            g_node = u.find('gloss')
            
            f = (f_node.text or "").strip() if f_node is not None else ""
            g = (g_node.text or "").strip() if g_node is not None else ""
            
            # Aplicamos negrita al morfema individual como pidió el tutor
            current_f_block += f"\\textbf{{{f}}}"
            current_g_block += g
            
            # ¿Es el final de una palabra?
            # Una palabra termina si:
            # 1. El morfema actual NO termina en '-'
            # 2. Y el SIGUIENTE morfema (si existe) NO empieza por '-'
            is_last = (i == len(units_m) - 1)
            next_f = units_m[i+1].find('form').text.strip() if not is_last and units_m[i+1].find('form') is not None else ""
            
            if not f.endswith('-') and not next_f.startswith('-'):
                # Cerramos el bloque de palabra y añadimos a la lista
                word_blocks_form.append(current_f_block)
                word_blocks_gloss.append(current_g_block)
                current_f_block = ""
                current_g_block = ""

        # Unimos con espacios (cada espacio separa una palabra para expex)
        forms_m = " ".join(word_blocks_form)
        glosses_m = " ".join(word_blocks_gloss)

        # 3. Análisis Sintáctico
        syntax_node = gloss.find('.//syntactic_analysis')
        syntax_content = ""
        if syntax_node is not None:
            parts = [f"{u.find('form').text.strip()} [\\textsc{{{u.find('gloss').text.strip()}}}]" 
                     for u in syntax_node.xpath('./unit') if u.find('form') is not None]
            syntax_content = " ".join(parts)

        # 4. Construcción del bloque LaTeX
        expex_block = [
            r'\ex',
            f"\\textit{{{translation}}} \\\\", 
            r'\begingl',
            f'\\gla {original} //',
            f'\\glb {forms_m} //',
            f'\\glc {glosses_m} //',
        ]
        if syntax_content:
            expex_block.append(f"\\glft \\textbf{{Sintaxis:}} {syntax_content} //")
        expex_block.append(r'\endgl')
        expex_block.append(r'\xe')
        
        self.doc.append(NoEscape("\n".join(expex_block) + "\n"))

    def save_tex(self, filename):
        self.doc.generate_tex(filename)