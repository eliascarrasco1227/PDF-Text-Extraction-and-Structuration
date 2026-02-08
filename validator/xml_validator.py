# validator/xml_validator.py
# pip install lxml

import logging
import io
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
        Retorna: (codigo, mensaje_error)
        """
        # Verificación de formación básica
        if XMLValidator.check_well_formed(xml_string) == -1:
            return -1, "Error de sintaxis: etiquetas mal cerradas o estructura XML inválida."

        try:
            with open(dtd_path, 'rb') as f:
                dtd_content = f.read()
            dtd = etree.DTD(io.BytesIO(dtd_content))
            root = etree.fromstring(xml_string.encode('utf-8'))
            
            if dtd.validate(root):
                return 1, "OK"
            else:
                # Capturamos el primer error del log para pasárselo a la IA
                error = dtd.error_log.filter_from_errors()[0]
                return 0, f"Error en línea {error.line}: {error.message}"
        except Exception as e:
            return -1, str(e)