import os
import time
from main import DocumentProcessor
from config.properties import PROMPT_PATH

# --- CONFIGURACIÓN DEL EXPERIMENTO ---
TEMPERATURES = [0.0, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0]
ITERATIONS = 5

# Definimos tus casos de test (Ruta del PDF, Páginas)
# Nota: Como main.py procesa lo que digan las propiedades, aquí trucaremos un poco
# pasando rutas de PDFs recortados (de una sola página) para ir más rápido.
TEST_CASES = [
    {
        "name": "Kaqchikel_146",
        "pdf": "data/reducidos/Gramatica-Normativa-Kaqchikel_pag_146.pdf" 
    },
    {
        "name": "Kaqchikel_172",
        "pdf": "data/reducidos/Gramatica-Normativa-Kaqchikel_pag_172.pdf"
    },
    {
        "name": "Kiche_43",
        # Asumo la ruta basada en tus archivos subidos, ajusta si es necesario
        "pdf": "data/reducidos/Gramatica-Normativa-Kiche_pag_44.pdf" # Ojo: ajusta al archivo correcto de la pag 43
    },
    {
        "name": "Mam_80",
        "pdf": "data/reducidos/Gramatica-Normativa-Mam_pag_80.pdf" # Asegúrate de tener este PDF reducido
    }
]

BASE_OUTPUT_DIR = "output/experiment_results"

def run_experiment():
    print(f"🚀 INICIANDO EXPERIMENTO MASIVO DE TEMPERATURAS")
    print(f"🌡️ Temperaturas: {TEMPERATURES}")
    print(f"📂 Casos de test: {len(TEST_CASES)}")
    print(f"🔄 Repeticiones por caso: {ITERATIONS}")
    print("--------------------------------------------------")

    total_runs = len(TEMPERATURES) * len(TEST_CASES) * ITERATIONS
    current_run = 0

    for temp in TEMPERATURES:
        # Carpeta específica para esta temperatura
        temp_dir = os.path.join(BASE_OUTPUT_DIR, f"temp_{str(temp).replace('.', '_')}")
        
        for case in TEST_CASES:
            # Subcarpeta para el archivo específico
            case_dir = os.path.join(temp_dir, case["name"])
            
            print(f"\n🌡️  Procesando Temperatura {temp} | Caso: {case['name']}")
            
            for i in range(1, ITERATIONS + 1):
                current_run += 1
                print(f"    ▶️ Ejecución {i}/{ITERATIONS} (Progreso Total: {current_run}/{total_runs})")
                
                try:
                    # Instanciamos el procesador con la configuración dinámica
                    processor = DocumentProcessor(
                        pdf_path=case["pdf"],
                        output_dir=case_dir,
                        temperature=temp
                    )
                    
                    # Ejecutamos
                    processor.process()
                    
                    # Pequeña pausa para no saturar la API (opcional)
                    time.sleep(2) 
                    
                except Exception as e:
                    print(f"    ❌ Error en ejecución {i}: {str(e)}")

    print("\n✅ EXPERIMENTO FINALIZADO")
    print(f"📁 Resultados guardados en: {BASE_OUTPUT_DIR}")

if __name__ == "__main__":
    run_experiment()