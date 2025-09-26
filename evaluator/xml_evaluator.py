import xml.etree.ElementTree as ET
from jiwer import wer, cer
from pathlib import Path

def extract_text_from_xml(xml_path: str) -> str:
    """
    Lee un archivo XML y extrae todo el texto de todos los elementos, 
    concatenándolo en una sola cadena.
    
    Args:
        xml_path: La ruta al archivo XML.
        
    Returns:
        Una cadena de texto con el contenido concatenado de todos los elementos.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Recorre todos los elementos y extrae el texto.
        # Usa ' '.join(t.strip() for t in root.itertext() if t.strip()) 
        # para manejar saltos de línea y espacios en blanco.
        text_content = ' '.join(root.itertext()).strip()
        
        # Limpia múltiples espacios en blanco creados por la concatenación de tags
        clean_text = ' '.join(text_content.split())
        
        return clean_text
    
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en la ruta: {xml_path}")
        return ""
    except ET.ParseError:
        print(f"Error: No se pudo parsear el archivo XML en la ruta: {xml_path}")
        return ""


def calculate_character_error_rate(reference_path: str, hypothesis_path: str) -> float:
    """
    Calcula la Tasa de Error de Carácter (CER) entre el contenido de dos archivos XML.
    
    Args:
        reference_path: Ruta al archivo XML de referencia (Ground Truth).
        hypothesis_path: Ruta al archivo XML generado (Output del modelo).
        
    Returns:
        El valor del CER (flotante entre 0 y 1).
    """
    
    # 1. Extraer el texto
    reference_text = extract_text_from_xml(reference_path)
    hypothesis_text = extract_text_from_xml(hypothesis_path)
    
    if not reference_text or not hypothesis_text:
        return -1.0 # Retorna un valor de error si la extracción falló
    
    # 2. Calcular el CER
    # CER = (Substituciones + Inserciones + Borrados) / Total de Caracteres de Referencia
    error_rate = cer(reference_text, hypothesis_text)
    
    return error_rate

# --- EJEMPLO DE USO ---

# Rutas de ejemplo (ajústalas a tu configuración real)
#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml"  # El XML generado por Gemini (Output)
#HYPOTHESIS_XML = "../output/6-pruebas_para_test_set/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml"  # El XML creado manualmente (Ground Truth)

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Mam_páginas_80-80_version_1.xml"  # El XML generado por Gemini (Output)
#HYPOTHESIS_XML = "../output/6-pruebas_para_test_set/Gramatica-Normativa-Mam_páginas_80-80_version_1.xml"  # El XML creado manualmente (Ground Truth)

REFERENCE_XML = "../output/6-pruebas_para_test_set/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml"  # El XML generado por Gemini (Output)
HYPOTHESIS_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml"  # El XML creado manualmente (Ground Truth)


if __name__ == '__main__':
    # Creamos archivos de ejemplo (deberías tenerlos de tu flujo de trabajo)
    # Suponemos que la "referencia" tiene el texto correcto
   
    # Cálculo
    cer_result = calculate_character_error_rate(REFERENCE_XML, HYPOTHESIS_XML)
    
    if cer_result >= 0:
        print("\n--- Resultado del Análisis CER ---")
        # print(f"Texto de Referencia (extraído): '{extract_text_from_xml(REFERENCE_XML)}'")
        # print(f"Texto de Hipótesis (extraído): '{extract_text_from_xml(HYPOTHESIS_XML)}'")
        print(f"\nCharacter Error Rate (CER): {cer_result:.4f}")
        print(f"Interpretación: Un valor de 0.0 es perfecto. Un valor de 1.0 es un 100% de error.")
        print(f"Similitud de los textos: {(1 - cer_result) * 100:.2f}%")
    else:
        print("El cálculo falló debido a errores de archivo o parseo.")