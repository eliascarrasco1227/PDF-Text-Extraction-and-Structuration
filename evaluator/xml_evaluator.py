import os
import glob
import re
from jiwer import cer
from pathlib import Path

try:
    from properties import EXPERIMENTS_DIR, TEST_CASE_MAPPING
except ImportError:
    print("❌ Error: Revisa properties.py")
    exit()


def get_raw_content_strict(file_path: str) -> str:
    path_obj = Path(file_path)
    if not path_obj.exists():
        return ""
    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'^```\w*\s*', '', content.strip())
        content = re.sub(r'```\s*$', '', content.strip())
        return content.strip()
    except Exception as e:
        print(f"❌ Error leyendo {path_obj.name}: {e}")
        return ""


def run_batch_evaluation():
    print(f"🚀 Iniciando evaluación desde: {EXPERIMENTS_DIR}\n")

    # 1. Precargar referencias
    print("--- Verificando Referencias ---")
    valid_references = {}
    for case_name, config in TEST_CASE_MAPPING.items():
        content = get_raw_content_strict(config["ref"])
        if content:
            print(f"✔ {case_name}: {len(content)} caracteres.")
            valid_references[case_name] = content
        else:
            print(f"❌ {case_name}: no encontrado en {config['ref']}")
    print("-" * 60 + "\n")

    results = []

    # 2. Iterar sobre cada carpeta temp_* que exista
    temp_dirs = sorted(glob.glob(os.path.join(EXPERIMENTS_DIR, "temp_*")))

    if not temp_dirs:
        print(f"❌ No se encontraron carpetas temp_* en: {EXPERIMENTS_DIR}")
        return

    for temp_dir in temp_dirs:
        temp_name = os.path.basename(temp_dir)

        for case_name, config in TEST_CASE_MAPPING.items():
            if case_name not in valid_references:
                continue

            ref_text = valid_references[case_name]
            prefix   = config["prefix"]

            # Buscar todos los .xml con el prefijo del caso en esta carpeta temp
            pattern    = os.path.join(temp_dir, f"{prefix}*.xml")
            xml_files  = sorted(glob.glob(pattern))

            if not xml_files:
                print(f"⚠ [{temp_name}] {case_name}: sin archivos (patrón: {pattern})")
                continue

            folder_cers = []
            folder_sims = []

            for xml_file in xml_files:
                hyp_text = get_raw_content_strict(xml_file)
                score = cer(ref_text, hyp_text) if hyp_text else 1.0
                folder_cers.append(score)
                folder_sims.append((1 - score) * 100)

            avg_cer = sum(folder_cers) / len(folder_cers)
            avg_sim = sum(folder_sims) / len(folder_sims)
            label   = f"(Promedio de {len(xml_files)} archivos)" if len(xml_files) > 1 else os.path.basename(xml_files[0])

            results.append({
                "Temp": temp_name,
                "Caso": case_name,
                "Archivo": label,
                "CER_Media": avg_cer,
                "Similitud_Media": avg_sim,
                "N": len(xml_files)
            })

    # 3. Tabla final
    print("\n" + "=" * 110)
    print(f"{'TEMP':<15} | {'CASO':<15} | {'SIMILITUD (Media)':<20} | {'CER (Media)':<12} | {'N':<3} | DETALLE")
    print("=" * 110)

    results.sort(key=lambda x: (x["Caso"], x["Temp"]))

    for r in results:
        sim_str = f"{r['Similitud_Media']:6.2f}%"
        cer_str = f"{r['CER_Media']:.4f}"
        if r['CER_Media'] >= 1.0:
            sim_str = "   0.00% ⚠️"
        print(f"{r['Temp']:<15} | {r['Caso']:<15} | {sim_str:<20} | {cer_str:<12} | {r['N']:<3} | {r['Archivo']}")


if __name__ == "__main__":
    run_batch_evaluation()