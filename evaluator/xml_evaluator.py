import os
import glob
import re
from jiwer import cer
from pathlib import Path

# Importación de configuración
try:
    from properties import EXPERIMENTS_DIR, TEST_CASE_MAPPING
except ImportError:
    print("❌ Error: Revisa properties.py para asegurar que EXPERIMENTS_DIR y TEST_CASE_MAPPING están definidos.")
    exit()

def get_raw_content_strict(file_path: str) -> str:
    """
    Lee el archivo tal cual es (Raw).
    Solo limpia los bloques de código Markdown para que la comparación sea justa
    con el contenido XML real.
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        return ""

    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            content = f.read()

        # --- LIMPIEZA ÚNICA: MARKDOWN ---
        # Solo quitamos ```xml al inicio y ``` al final.
        # Todo lo demás (etiquetas, espacios, saltos de línea) SE MANTIENE para el CER.
        content = re.sub(r'^```\w*\s*', '', content.strip()) # Quita ```xml del inicio
        content = re.sub(r'```\s*$', '', content.strip())    # Quita ``` del final
        
        return content.strip() # Un strip final por seguridad

    except Exception as e:
        print(f"❌ Error leyendo {path_obj.name}: {e}")
        return ""

def run_batch_evaluation():
    print(f"🚀 Iniciando Evaluación ESTRICTA (Raw XML) desde: {EXPERIMENTS_DIR}\n")
    results = []
    
    # 1. Verificación de Referencias
    print("--- Verificando Referencias ---")
    for case, ref in TEST_CASE_MAPPING.items():
        content = get_raw_content_strict(ref)
        if content:
            print(f"✔ {case}: Referencia cargada ({len(content)} caracteres).")
        else:
            print(f"❌ {case}: Referencia VACÍA o no encontrada en {ref}")
    print("-" * 50 + "\n")

    # 2. Bucle de Evaluación
    for case_folder_name, reference_path in TEST_CASE_MAPPING.items():
        # Busca en todas las carpetas de temperatura
        search_pattern = os.path.join(EXPERIMENTS_DIR, "temp_*", case_folder_name, "*.xml")
        found_files = glob.glob(search_pattern)

        if not found_files:
            continue

        # Cargamos el texto de referencia UNA vez por caso
        ref_text = get_raw_content_strict(reference_path)
        if not ref_text: continue # Si falla la ref, saltamos

        for hypothesis_path in found_files:
            try:
                # Extraer info del path
                path_parts = os.path.normpath(hypothesis_path).split(os.sep)
                temp_name = path_parts[-3] 
                file_name = os.path.basename(hypothesis_path)

                # --- CÁLCULO CER ESTRICTO ---
                hyp_text = get_raw_content_strict(hypothesis_path)
                
                if not hyp_text:
                    score = 1.0 # Archivo vacío o ilegible
                else:
                    score = cer(ref_text, hyp_text)

                # Guardamos
                results.append({
                    "Temp": temp_name,
                    "Caso": case_folder_name,
                    "Archivo": file_name,
                    "CER": score,
                    "Similitud %": (1 - score) * 100
                })

            except Exception as e:
                print(f"❌ Error en {file_name}: {e}")

    # 3. Tabla Final
    print("\n" + "="*100)
    print(f"{'TEMP':<15} | {'CASO':<15} | {'SIMILITUD (ESTRICTA)':<22} | {'CER':<8} | {'ARCHIVO'}")
    print("="*100)
    
    # Ordenar: Caso -> Mejor Similitud
    results.sort(key=lambda x: (x["Caso"], -x["Similitud %"]))

    for r in results:
        # Formateo visual
        sim_str = f"{r['Similitud %']:6.2f}%"
        if r['Similitud %'] < 0: sim_str = "   0.00% (Neg)" # CER > 1 da sim negativa
        if r['CER'] == 1.0: sim_str = "   0.00% ⚠️"

        print(f"{r['Temp']:<15} | {r['Caso']:<15} | {sim_str:<22} | {r['CER']:.4f}   | {r['Archivo']}")

if __name__ == "__main__":
    run_batch_evaluation()