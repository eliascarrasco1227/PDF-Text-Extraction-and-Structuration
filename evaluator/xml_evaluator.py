import os
import glob
import re
from jiwer import cer
from pathlib import Path

# Intentamos importar la configuración
try:
    from properties import EXPERIMENTS_DIR, TEST_CASE_MAPPING
except ImportError:
    print("❌ Error: Revisa properties.py para asegurar que EXPERIMENTS_DIR y TEST_CASE_MAPPING están definidos.")
    exit()

def get_raw_content_strict(file_path: str) -> str:
    """
    Lee el archivo tal cual es (Raw) para una evaluación estricta.
    Solo limpia los bloques de código Markdown (```xml) iniciales/finales.
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        return ""

    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            content = f.read()

        # Limpieza mínima: Solo quitamos el "envoltorio" de markdown si existe
        content = re.sub(r'^```\w*\s*', '', content.strip()) 
        content = re.sub(r'```\s*$', '', content.strip())
        
        return content.strip()

    except Exception as e:
        print(f"❌ Error leyendo {path_obj.name}: {e}")
        return ""

def run_batch_evaluation():
    print(f"🚀 Iniciando Evaluación AGRUPADA (Promedio por Carpeta) desde: {EXPERIMENTS_DIR}\n")
    results = []
    
    # 1. Verificación de Referencias
    print("--- Verificando Referencias ---")
    valid_references = {}
    for case, ref_path in TEST_CASE_MAPPING.items():
        content = get_raw_content_strict(ref_path)
        if content:
            print(f"✔ {case}: Referencia cargada ({len(content)} caracteres).")
            valid_references[case] = content # Guardamos el texto en memoria para no leerlo mil veces
        else:
            print(f"❌ {case}: Referencia VACÍA o no encontrada en {ref_path}")
    print("-" * 60 + "\n")

    # 2. Bucle de Evaluación Agrupada
    for case_folder_name, ref_text in valid_references.items():
        
        # Paso A: Encontrar todas las carpetas de este caso (una por temperatura)
        # Patrón: ../output/.../temp_*/Caso_X/
        case_dirs_pattern = os.path.join(EXPERIMENTS_DIR, "temp_*", case_folder_name)
        found_dirs = glob.glob(case_dirs_pattern)

        if not found_dirs:
            continue

        for specific_case_dir in found_dirs:
            # Paso B: Identificar la temperatura
            # La ruta es algo como: .../temp_0_1/Kaqchikel_146
            # El padre es .../temp_0_1, extraemos el nombre base del padre
            parent_dir = os.path.dirname(specific_case_dir)
            temp_name = os.path.basename(parent_dir)

            # Paso C: Buscar todos los XMLs DENTRO de esa carpeta específica
            xml_files = glob.glob(os.path.join(specific_case_dir, "*.xml"))
            
            if not xml_files:
                continue

            # Paso D: Calcular métricas para cada archivo individualmente
            folder_cers = []
            folder_sims = []

            for xml_file in xml_files:
                hyp_text = get_raw_content_strict(xml_file)
                
                if not hyp_text:
                    score = 1.0 # Archivo vacío o roto = 100% error
                else:
                    score = cer(ref_text, hyp_text)
                
                folder_cers.append(score)
                folder_sims.append((1 - score) * 100)

            # Paso E: Calcular MEDIAS
            if folder_cers:
                avg_cer = sum(folder_cers) / len(folder_cers)
                avg_sim = sum(folder_sims) / len(folder_sims)
                
                # Nombre del archivo para mostrar
                if len(xml_files) > 1:
                    file_label = f"(Promedio de {len(xml_files)} archivos)"
                else:
                    file_label = os.path.basename(xml_files[0]) # Si solo hay uno, ponemos su nombre

                results.append({
                    "Temp": temp_name,
                    "Caso": case_folder_name,
                    "Archivo": file_label,
                    "CER_Media": avg_cer,
                    "Similitud_Media": avg_sim,
                    "N": len(xml_files)
                })

    # 3. Tabla Final
    print("\n" + "="*110)
    print(f"{'TEMP':<15} | {'CASO':<15} | {'SIMILITUD (Media)':<20} | {'CER (Media)':<12} | {'N':<3} | {'DETALLE'}")
    print("="*110)
    
    # Ordenamos: Primero Caso, luego mejor Similitud
    results.sort(key=lambda x: (x["Caso"], -x["Similitud_Media"]))

    for r in results:
        sim_str = f"{r['Similitud_Media']:6.2f}%"
        cer_str = f"{r['CER_Media']:.4f}"
        
        # Marcamos visualmente si es negativo o error total
        if r['Similitud_Media'] < 0: sim_str = "   0.00% (Neg)"
        if r['CER_Media'] >= 1.0: sim_str = "   0.00% ⚠️"

        print(f"{r['Temp']:<15} | {r['Caso']:<15} | {sim_str:<20} | {cer_str:<12} | {r['N']:<3} | {r['Archivo']}")

if __name__ == "__main__":
    run_batch_evaluation()