import time
import os
import re
from main import DocumentProcessor
from evaluator.single_evaluator import calculate_character_error_rate
from core.logger_config import app_logger

# CONFIGURACIÓN DEL EXPERIMENTO
# Formato: (Nombre_PDF, Pagina_Inicio, Pagina_Fin, XML_Referencia)
EXPERIMENTOS = [
    ("Gramatica-Normativa-Kaqchikel_pag_172.pdf", 172, 172, "test_set/Gramatica-Normativa-Kaqchikel_páginas_172.xml"),
    ("Gramatica-Normativa-Mam_pag_80.pdf", 80, 80, "test_set/Gramatica-Normativa-Mam_páginas_80.xml"),
]

VERSIONES = 3 

def run_benchmarks():
    logger = app_logger
    print(f"\n{'PÁGINA':<35} | {'V1':<8} | {'V2':<8} | {'V3':<8} | {'MEDIA'}")
    print("-" * 85)

    for pdf_name, p_start, p_end, ref_path in EXPERIMENTOS:
        pdf_path = os.path.join("data/reducidos", pdf_name)
        resultados_similitud = []

        if not os.path.exists(ref_path):
            print(f"⚠️ Error: No existe la referencia {ref_path}. Saltando...")
            continue

        for v in range(VERSIONES):
            try:
                # Ejecutamos el procesador normal
                # Asegúrate de que en config/properties.py PAGINAS esté configurado 
                # para la página que quieres testear antes de lanzar esto, 
                # o que DocumentProcessor acepte el rango.
                processor = DocumentProcessor(pdf_path=pdf_path)
                xml_generado_path = processor.process() 
                
                # Calculamos similitud usando la función puente
                cer_val = calculate_character_error_rate(ref_path, xml_generado_path)
                
                if cer_val is not None:
                    similitud = (1 - cer_val) * 100
                    resultados_similitud.append(similitud)
                else:
                    resultados_similitud.append(0.0)

                time.sleep(5) # Delay para evitar 429 Resource Exhausted

            except Exception as e:
                print(f"❌ Error en {pdf_name} V{v+1}: {str(e)}")
                resultados_similitud.append(0.0)

        # Rellenar con 0 si algo falló para que la tabla no se rompa
        while len(resultados_similitud) < VERSIONES:
            resultados_similitud.append(0.0)

        media = sum(resultados_similitud) / VERSIONES
        v1, v2, v3 = resultados_similitud
        
        nombre_fila = f"{pdf_name} (P{p_start})"
        print(f"{nombre_fila:<35} | {v1:>7.1f}% | {v2:>7.1f}% | {v3:>7.1f}% | {media:>7.1f}%")

if __name__ == "__main__":
    run_benchmarks()