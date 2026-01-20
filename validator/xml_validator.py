# validator/xml_validator.py
# pip install lxml

import logging
from lxml import etree
from io import BytesIO

class XMLValidator:
    """
    Módulo encargado de verificar la calidad técnica del XML generado por la IA.
    """

    @staticmethod
    def check_well_formed(xml_string):
        """
        Comprueba si el XML está bien formado (sintaxis básica).
        Retorna:
             1: Si está bien formado.
            -1: Si hay errores de sintaxis (etiquetas sin cerrar, etc.).
        """
        if not xml_string or not isinstance(xml_string, str):
            return -1
        
        try:
            # Intentamos parsear el string
            etree.fromstring(xml_string.encode('utf-8'))
            return 1
        except etree.XMLSyntaxError as e:
            logging.error(f"Error de sintaxis XML: {e}")
            return -1

    @staticmethod
    def check_valid(xml_string, dtd_path):
        """
        Comprueba si el XML es válido según un archivo DTD.
        Retorna:
             1: Si es válido.
             0: Si está bien formado pero NO cumple el DTD.
            -1: Si ni siquiera está bien formado.
        """
        # Primero verificamos si está bien formado
        if XMLValidator.check_well_formed(xml_string) == -1:
            return -1

        try:
            # Cargamos el DTD
            with open(dtd_path, 'rb') as f:
                dtd_content = f.read()
            dtd = etree.DTD(BytesIO(dtd_content))

            # Parseamos el XML para validarlo
            root = etree.fromstring(xml_string.encode('utf-8'))
            
            if dtd.validate(root):
                return 1
            else:
                logging.warning(f"XML bien formado pero INVÁLIDO según DTD: {dtd.error_log.filter_from_errors()}")
                return 0
                
        except Exception as e:
            logging.error(f"Error durante la validación DTD: {e}")
            return 0