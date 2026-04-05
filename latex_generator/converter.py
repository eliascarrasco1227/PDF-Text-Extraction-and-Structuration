import os
import re
from lxml import etree
from pylatex import Document, Section, Subsection, Command, NoEscape
from pylatex.utils import bold, italic
from core.logger_config import app_logger

class XMLToLaTeXConverter:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.logger = app_logger
        self.doc = Document(default_filepath='output_latex')
        self._setup_preamble()

    def _setup_preamble(self):
        """Configuración necesaria para lingüística y caracteres especiales"""
        self.doc.packages.append(Command('usepackage', 'expex'))
        self.doc.packages.append(Command('usepackage', 'geometry'))
        self.doc.packages.append(Command('geometry', 'margin=2cm'))
        self.doc.preamble.append(NoEscape(r'\lingset{everygla=\it}'))

    def _clean_for_latex(self, text: str) -> str:
        """Limpia caracteres Unicode problemáticos y escapa caracteres especiales"""
        if not text:
            return ""
        
        # 1. Corrección de números Unicode (U+06F0 y similares)
        replacements = {
            '\u06f0': '0', '\u06f1': '1', '\u06f2': '2', '\u06f3': '3', 
            '\u06f4': '4', '\u06f5': '5', '\u06f6': '6', '\u06f7': '7', 
            '\u06f8': '8', '\u06f9': '9',
            '\u200b': '', '\u200e': '', '\u200f': '', 
        }
        for char, rep in replacements.items():
            text = text.replace(char, rep)

        # 2. Escapar caracteres reservados de LaTeX
        text = text.replace('_', r'\_').replace('$', r'\$').replace('%', r'\%')
        
        return text.strip()

    def parse_and_generate(self):
        """Punto de entrada principal para el procesamiento"""
        try:
            tree = etree.parse(self.xml_path)
            root = tree.getroot()

            source = root.get('source', 'Unknown')
            pages = root.get('pages', 'N/A')
            
            self.doc.preamble.append(Command('title', f'Análisis Lingüístico: {source}'))
            self.doc.preamble.append(Command('author', f'Páginas: {pages}'))
            self.doc.append(NoEscape(r'\maketitle'))

            for page in root.findall('page'):
                page_num = page.get('number', '?')
                self.doc.append(Section(f'Page {page_num}'))
                self._process_elements(page)

            self.logger.info(f"🌳 XML parseado con éxito: {self.xml_path}")
        except Exception as e:
            self.logger.error(f"❌ Error al parsear XML: {str(e)}")
            raise

    def _process_elements(self, container):
        """Procesa los elementos de forma secuencial (Estructura Plana)"""
        for element in container:
            tag = element.tag
            text = (element.text or "").strip()

            if tag == 'heading':
                if text:
                    self.doc.append(Subsection(self._clean_for_latex(text)))
            elif tag == 'title':
                if text:
                    self.doc.append(Command('centerline', bold(self._clean_for_latex(text))))
            elif tag == 'line':
                if text:
                    self.doc.append(self._clean_for_latex(text) + " ")
            elif tag == 'interlinear_gloss':
                self._process_gloss(element)

    def _process_gloss(self, gloss_node):
        """Genera el bloque expex para las glosas interlineales"""
        # 1. Parallel Phrase
        p_phrase = gloss_node.find('parallel_phrase')
        original = ""
        translation = ""
        if p_phrase is not None:
            original = (p_phrase.findtext('original') or "").strip()
            translation = (p_phrase.findtext('translation') or "").strip()

        # 2. Morpheme Analysis
        m_analysis = gloss_node.find('morpheme_analysis')
        morph_forms = []
        morph_glosses_formatted = []
        if m_analysis is not None:
            for unit in m_analysis.findall('unit'):
                f = (unit.findtext('form') or "").strip()
                g = (unit.findtext('gloss') or "").strip()
                if f:
                    morph_forms.append(self._clean_for_latex(f))
                    # Aplicamos negrita aquí para evitar el error de backslash en f-string
                    g_clean = self._clean_for_latex(g)
                    morph_glosses_formatted.append(f"\\textbf{{{g_clean}}}")

        # 3. Syntactic Analysis
        s_analysis = gloss_node.find('syntactic_analysis')
        syntax_units = []
        if s_analysis is not None:
            for unit in s_analysis.findall('unit'):
                f = (unit.findtext('form') or "").strip()
                g = (unit.findtext('gloss') or "").strip()
                if f:
                    f_c = self._clean_for_latex(f)
                    g_c = self._clean_for_latex(g)
                    syntax_units.append(f"[{f_c}]_{{{g_c}}}")

        # Unimos las listas fuera de las f-strings
        forms_str = " ".join(morph_forms)
        glosses_str = " ".join(morph_glosses_formatted)
        syntax_str = " ".join(syntax_units)

        # Construir el bloque LaTeX ExPex
        expex_block = [r'\ex']
        
        expex_block.append(f'  \u0009abla {original}' if original else '  \u0009abla ')
        
        if forms_str:
            expex_block.append(f'  \u0009ablz {forms_str}')
            
        if glosses_str:
            expex_block.append(f'  \u0009able {glosses_str}')
        
        if syntax_str:
            expex_block.append(f'  \u0009ablf {syntax_str}')
        
        if translation:
            t_clean = self._clean_for_latex(translation)
            expex_block.append(f'  \\xe[\\textit{{{t_clean}}}]')
        else:
            expex_block.append(r'  \xe')

        self.doc.append(NoEscape("\n".join(expex_block) + "\n"))

    def save_tex(self, output_path):
        """Guarda el archivo .tex final"""
        self.doc.generate_tex(output_path)