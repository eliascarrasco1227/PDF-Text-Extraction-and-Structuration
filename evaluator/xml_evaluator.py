import xml.etree.ElementTree as ET
from jiwer import cer
from pathlib import Path
# Asumo que 'properties' contiene las rutas correctas
from properties import REFERENCE_XML, HYPOTHESIS_XML 

def extract_text_from_xml(xml_path: str) -> str:
    """
    Lee un archivo XML y extrae todo el texto de todos los elementos, 
    concatenándolo en una sola cadena.
    """
    try:
        # Usamos Path para manejar la ruta fácilmente
        xml_path = Path(xml_path) 
        
        # Comprobación de existencia fuera del parseo para un mejor manejo de errores
        if not xml_path.exists():
            print(f"Error: Archivo no encontrado en la ruta: {xml_path}")
            return ""

        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        text_content = ' '.join(root.itertext()).strip()
        clean_text = ' '.join(text_content.split())
        
        return clean_text
    
    except ET.ParseError:
        print(f"Error: No se pudo parsear el archivo XML en la ruta: {xml_path}")
        return ""


def find_hypothesis_files(base_hypothesis_path: str) -> list[str]:
    """
    Encuentra el archivo de hipótesis base y todas sus versiones.
    
    Args:
        base_hypothesis_path: La ruta base del archivo (e.g., ".../file.xml").
        
    Returns:
        Una lista de rutas de archivos de hipótesis encontrados.
    """
    base_path = Path(base_hypothesis_path)
    
    # 1. Obtenemos el directorio y el nombre del archivo base sin la extensión
    parent_dir = base_path.parent
    base_stem = base_path.stem
    
    # 2. Creamos el patrón de búsqueda: busca el nombre base y cualquier cosa que empiece 
    # con el nombre base seguido de un guion bajo, y termine en .xml.
    # Esto incluye el archivo base (si no tiene nada más) y todas las versiones.
    search_pattern = f"{base_stem}*.xml"
    
    # 3. Usamos glob para buscar todos los archivos que coincidan
    found_files = list(parent_dir.glob(search_pattern))
    
    # Convertimos los objetos Path a strings para compatibilidad con el resto del código
    return [str(f) for f in found_files]


def calculate_character_error_rate(reference_path: str, base_hypothesis_path: str) -> dict:
    """
    Calcula la Tasa de Error de Carácter (CER) para una referencia contra 
    múltiples archivos de hipótesis (base + versiones).
    
    Args:
        reference_path: Ruta al archivo XML de referencia (Ground Truth).
        base_hypothesis_path: Ruta base del archivo XML generado.
        
    Returns:
        Un diccionario con el CER para cada archivo de hipótesis encontrado.
    """
    
    # 1. Extraer el texto de referencia UNA SOLA VEZ
    reference_text = extract_text_from_xml(reference_path)
    if not reference_text:
        return {"Error": "No se pudo extraer el texto de referencia."}

    # 2. Encontrar todos los archivos de hipótesis
    hypothesis_paths = find_hypothesis_files(base_hypothesis_path)
    
    if not hypothesis_paths:
        return {"Error": f"No se encontraron archivos de hipótesis con el prefijo: {base_hypothesis_path}"}
    
    results = {}
    
    # 3. Iterar sobre todos los archivos de hipótesis y calcular el CER
    for h_path in hypothesis_paths:
        # Extraer el texto de la hipótesis
        hypothesis_text = extract_text_from_xml(h_path)
        
        if not hypothesis_text:
            results[h_path] = -1.0
            continue 
        
        # Calcular el CER
        # CER = (Substituciones + Inserciones + Borrados) / Total de Caracteres de Referencia
        error_rate = cer(reference_text, hypothesis_text)
        
        # Guardar el resultado en el diccionario, usando el nombre del archivo como clave
        results[Path(h_path).name] = error_rate
        
    return results

if __name__ == '__main__':
    # --- SIMULACIÓN DE RUTAS ---
    # NOTA: Debes asegurar que los valores de REFERENCE_XML e HYPOTHESIS_XML
    # en tu 'properties.py' apunten a rutas válidas para el test.
    
    # Asumimos que REFERENCE_XML y HYPOTHESIS_XML son strings
    # Ejemplo de cómo se verían en 'properties.py':
    # REFERENCE_XML = "../data/Ground_Truth/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml"
    # HYPOTHESIS_XML = "../output/6-pruebas_para_test_set/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml"

    # --- Ejecución del Cálculo ---
    all_cer_results = calculate_character_error_rate(REFERENCE_XML, HYPOTHESIS_XML)
    
    print("\n--- Resultados del Análisis CER para Múltiples Hipótesis ---")
    
    if isinstance(all_cer_results, dict) and "Error" in all_cer_results:
        print(all_cer_results["Error"])
    else:
        for filename, cer_result in all_cer_results.items():
            if cer_result >= 0:
                print(f"\nArchivo Hipótesis: {filename}")
                print(f"  Character Error Rate (CER): {cer_result:.4f}")
                print(f"  Similitud del Texto: {(1 - cer_result) * 100:.2f}%")
            else:
                print(f"\nArchivo Hipótesis: {filename}")
                print("  El cálculo falló (error de parseo o archivo no encontrado).")