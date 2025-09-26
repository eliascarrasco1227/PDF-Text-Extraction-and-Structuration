import xml.etree.ElementTree as ET
import lxml.etree as etree # Necesario para el parsing robusto
from jiwer import cer
from pathlib import Path
import re 
from properties import REFERENCE_XML, HYPOTHESIS_XML 

def extract_text_from_xml(xml_path: str) -> str:
    """
    Lee un archivo XML de forma robusta usando lxml para intentar la recuperación
    en caso de errores de parseo.
    """
    xml_path = Path(xml_path) 
    if not xml_path.exists():
        print(f"Error: Archivo no encontrado en la ruta: {xml_path}")
        return ""
        
    try:
        # 1. Leer el contenido como una cadena
        with open(xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        # 2. Reemplazar caracteres problemáticos comunes ANTES del parseo.
        # Esto es una limpieza preventiva, pero el parser de lxml con recover=True
        # es el mecanismo principal de robustez.
        xml_content = xml_content.replace('&', '&amp;')
        
        # 3. Usar lxml con el parser de recuperación (RECOVERY)
        parser = etree.XMLParser(recover=True, encoding='utf-8')
        
        # 4. Parsear desde la cadena de texto
        root = etree.fromstring(xml_content.encode('utf-8'), parser=parser)
        
        # 5. Extraer el texto de forma recursiva
        text_content = ' '.join(root.itertext()).strip()
        clean_text = ' '.join(text_content.split())
        
        return clean_text
    
    except Exception as e:
        # Captura cualquier error de lxml o IO
        print(f"Error: No se pudo parsear (o leer) el archivo XML en la ruta: {xml_path}.")
        # El detalle exacto del error se ha quitado aquí, ya que el usuario lo ha visto
        return ""


def get_hypothesis_paths(base_hypothesis_path: str) -> list[str]:
    """
    Determina si la ruta es un archivo exacto (.xml) o una base para buscar
    múltiples versiones.

    Args:
        base_hypothesis_path: La ruta o prefijo base proporcionado.
        
    Returns:
        Una lista de rutas de archivos de hipótesis encontrados.
    """
    base_path = Path(base_hypothesis_path)

    # Lógica 1: Si la ruta termina en '.xml', tratarla como un archivo único.
    if base_path.suffix == '.xml':
        if base_path.exists():
            return [str(base_path)]
        else:
            print(f"Advertencia: Archivo único especificado no encontrado: {base_hypothesis_path}")
            return []

    # Lógica 2 (La que se usaba antes): Si no termina en '.xml', buscar con comodín.
    else:
        parent_dir = base_path.parent
        # Usamos el nombre base como prefijo para la búsqueda
        base_name_prefix = base_path.name 
        
        # Patrón de búsqueda: el prefijo seguido de cualquier cosa y terminando en .xml
        search_pattern = f"{base_name_prefix}*.xml"
        
        # Búsqueda recursiva o no, dependiendo de la estructura de tu proyecto.
        # Usaremos glob() para buscar solo en el directorio padre,
        # lo que es más eficiente y suele ser suficiente para proyectos estructurados.
        found_files = list(parent_dir.glob(search_pattern))
        
        # Si no se encuentra ningún archivo, intentar buscar con la ruta completa como comodín
        if not found_files:
             # Esto intenta cubrir el caso donde el prefijo dado está en el mismo nivel
             # pero no termina en la extensión.
             search_pattern = f"{base_path.name}*.xml"
             found_files = list(parent_dir.glob(search_pattern))

        return [str(f) for f in found_files]


def calculate_character_error_rate(reference_path: str, base_hypothesis_path: str) -> dict:
    """
    Calcula la Tasa de Error de Carácter (CER) para una referencia contra 
    uno o múltiples archivos de hipótesis.
    """
    
    # 1. Extraer el texto de referencia UNA SOLA VEZ
    reference_text = extract_text_from_xml(reference_path)
    if not reference_text:
        return {"Error": "No se pudo extraer el texto de referencia."}

    # 2. Obtener la lista de archivos de hipótesis usando la nueva lógica
    hypothesis_paths = get_hypothesis_paths(base_hypothesis_path)
    
    if not hypothesis_paths:
        return {"Error": f"No se encontraron archivos de hipótesis para la ruta/prefijo: {base_hypothesis_path}"}
    
    results = {}
    
    # 3. Iterar sobre todos los archivos encontrados y calcular el CER
    for h_path in hypothesis_paths:
        # Extraer el texto de la hipótesis
        hypothesis_text = extract_text_from_xml(h_path)
        
        # Manejar el caso de error de parseo que está capturado dentro de extract_text_from_xml
        if not hypothesis_text:
            results[Path(h_path).name] = -1.0
            continue 
        
        # Calcular el CER
        error_rate = cer(reference_text, hypothesis_text)
        
        # Guardar el resultado en el diccionario
        results[Path(h_path).name] = error_rate
        
    return results

if __name__ == '__main__':
    
    # --- Ejecución del Cálculo ---
    all_cer_results = calculate_character_error_rate(REFERENCE_XML, HYPOTHESIS_XML)
    
    print("\n--- Resultados del Análisis CER para Hipótesis ---")
    
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