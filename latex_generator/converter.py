import os
from lxml import etree
from pylatex import Document, Section, Subsection, Command, NoEscape
from pylatex.utils import bold
from core.logger_config import app_logger
from config.properties import PDF_PATH

class XMLToLaTeXConverter:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.logger = app_logger
        self.doc = Document(default_filepath='output_latex', geometry_options={"margin": "2cm"})
        self._setup_preamble()

    def _setup_preamble(self):
        """Configuración para lingüística y paquetes básicos"""
        self.doc.packages.append(Command('usepackage', 'expex'))
        self.doc.packages.append(Command('usepackage[T1]', 'fontenc'))
        self.doc.packages.append(Command('usepackage[utf8]', 'inputenc'))
        self.doc.packages.append(Command('usepackage', 'babel', 'spanish'))

    def _clean_for_latex(self, text: str) -> str:
        """Limpia caracteres Unicode y escapa reservados"""
        if not text: return ""
        replacements = {
            '\u06f0': '0', '\u06f1': '1', '\u06f2': '2', '\u06f3': '3', 
            '\u06f4': '4', '\u06f5': '5', '\u06f6': '6', '\u06f7': '7', 
            '\u06f8': '8', '\u06f9': '9',
            '\u200b': '', '\u200e': '', '\u200f': '', 
        }
        for char, rep in replacements.items():
            text = text.replace(char, rep)
        
        # Escapado básico de caracteres reservados
        return text.replace('_', r'\_').replace('$', r'\$').replace('%', r'\%').strip()

    def getTitle(self, path):
        """Extrae el título del PDF desde la ruta"""
        filename = os.path.splitext(os.path.basename(path))[0]
        return filename.split('_pag_')[0].replace('-', ' ')

    def parse_and_generate(self):
        """Procesa el XML con etiquetas en inglés y genera el PDF"""
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(self.xml_path, parser)
            root = tree.getroot()

            source = root.get('source', self.getTitle(PDF_PATH))
            self.doc.preamble.append(Command('title', f"Análisis Lingüístico: {source}"))
            self.doc.preamble.append(Command('author', 'Generado por el TFM de Elías Carrasco'))
            self.doc.append(NoEscape(r'\maketitle'))

            for page in root.findall('page'):
                num_pag = page.get('number', '?')
                with self.doc.create(Section(f"Page {num_pag}")):
                    self._process_elements(page)

            self.logger.info(f"🌳 XML procesado correctamente: {self.xml_path}")
        except Exception as e:
            self.logger.error(f"❌ Error en parse_and_generate: {str(e)}")
            raise

    def _process_elements(self, container):
        """Recorre los elementos según el esquema inglés"""
        for element in container:
            tag = element.tag
            text = (element.text or "").strip()

            if tag == 'heading':
                self.doc.append(Subsection(self._clean_for_latex(text)))
            elif tag == 'title':
                self.doc.append(Command('centerline', bold(self._clean_for_latex(text))))
            elif tag == 'line':
                if text: self.doc.append(self._clean_for_latex(text) + " ")
            elif tag == 'interlinear_gloss':
                self.doc.append(NoEscape(r'\par\medskip'))
                self._process_gloss(element)
                self.doc.append(NoEscape(r'\medskip'))

    def _process_gloss(self, gloss_node):
        """Lógica restaurada de alineación vertical (ExPex)"""
        # 1. Extraer Original y Traducción
        p_phrase = gloss_node.find('parallel_phrase')
        original = (p_phrase.findtext('original') or "").strip() if p_phrase is not None else ""
        translation = (p_phrase.findtext('translation') or "").strip() if p_phrase is not None else ""

        # 2. Reconstruir lógica de morfemas (Agrupamiento por palabras)
        units_m = gloss_node.xpath('.//morpheme_analysis/unit')
        word_blocks_form = []
        word_blocks_gloss = []
        
        current_f_block = ""
        current_g_block = ""

        for i, u in enumerate(units_m):
            f = (u.findtext('form') or "").strip()
            g = (u.findtext('gloss') or "").strip()
            
            # Formateo de morfemas (negrita en la glosa según versión previa)
            current_f_block += f
            current_g_block += f"\\textbf{{{self._clean_for_latex(g)}}}"
            
            # Lógica de guiones para saber si la palabra continúa
            is_last = (i == len(units_m) - 1)
            next_f = (units_m[i+1].findtext('form') or "").strip() if not is_last else ""
            
            # Si el morfema actual no termina en '-' y el siguiente no empieza con '-', es fin de palabra
            if not f.endswith('-') and not next_f.startswith('-'):
                word_blocks_form.append(current_f_block)
                word_blocks_gloss.append(current_g_block)
                current_f_block = ""
                current_g_block = ""

        forms_m = " ".join(word_blocks_form)
        glosses_m = " ".join(word_blocks_gloss)

        # 3. Análisis Sintáctico (estilo subscript como pediste)
        s_analysis = gloss_node.find('syntactic_analysis')
        syntax_content = ""
        if s_analysis is not None:
            parts = []
            for u in s_analysis.findall('unit'):
                sf = self._clean_for_latex(u.findtext('form') or "")
                sg = self._clean_for_latex(u.findtext('gloss') or "")
                if sf: parts.append(f"[{sf}]\\textsubscript{{{sg}}}")
            syntax_content = " ".join(parts)

        # 4. Construcción del Bloque ExPex (Regreso a \begingl \endgl)
        expex_block = [
            r'\ex',
            f"\\textit{{{self._clean_for_latex(translation)}}} \\\\",
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

    def save_tex(self, output_path):
        self.doc.generate_tex(output_path)