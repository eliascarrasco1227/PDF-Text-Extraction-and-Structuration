# Pruebas
#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml" 
#HYPOTHESIS_XML = "../output/6-pruebas_para_test_set/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml"  

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Mam_páginas_80-80_version_1.xml" 
#HYPOTHESIS_XML = "../output/6-pruebas_para_test_set/Gramatica-Normativa-Mam_páginas_80-80_version_1.xml"  

#REFERENCE_XML = "../output/6-pruebas_para_test_set/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml" 
#HYPOTHESIS_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml"  


# Bucle
#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml" 
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/Gramatica-Normativa-Kiche_páginas_43-43/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml"  

# Si le pasas un directorio, devuelve la media de todos. 
# Si le pasas un xml devuelve su similitud.
#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml" 
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/Gramatica-Normativa-Kiche_páginas_43-43/Gramatica-Normativa-Kiche_páginas_43-43"  

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml" 
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/Gramatica-Normativa-Kiche_páginas_43-43/Gramatica-Normativa-Kiche_páginas_43-43"  

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml" 
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/Gramatica-Normativa-Kaqchikel_páginas_146-146/Gramatica-Normativa-Kaqchikel_páginas_146-146"  

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Mam_páginas_80-80_version_1.xml" 
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/Gramatica-Normativa-Mam_páginas_80-80/Gramatica-Normativa-Mam_páginas_80-80"  


#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_146-146.xml" 
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/few-shot/Gramatica-Normativa-Kaqchikel_pag_146_páginas_1-1"  


#REFERENCE_XML = "../test_set/Gramatica-Normativa-Mam_páginas_80-80_version_1.xml"
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/few-shot-mam/Gramatica-Normativa"


#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_172.xml"
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/zero-shot-Kaqchikel_pag_147/G"

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml"
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/few-shot-kiche/G"

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_172.xml"
#HYPOTHESIS_XML = "../output/9-doble_few_shot/Kaqchikel_146/G"

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43.xml"
#HYPOTHESIS_XML = "../output/9-doble_few_shot/Kiche/G"



#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_172.xml"
#HYPOTHESIS_XML = "../output/experiment_results/temp_0_0/Kaqchikel_172/G"

REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43.xml"
HYPOTHESIS_XML = "../output/Gramatica-Normativa-Kiche_pag_44_páginas_1-1_version_7.xml"



import os

# --- NUEVA CONFIGURACIÓN PARA EVALUACIÓN MASIVA ---

# Ruta base donde están todas las carpetas de temperaturas (temp_0_1, temp_0_5, etc.)
EXPERIMENTS_DIR = os.path.join("..", "output", "experiment_results")

# Mapeo: "Nombre de la carpeta del caso" -> "Ruta del XML de Referencia (Gold Standard)"
# Asegúrate de que las rutas relativas apuntan correctamente a tu carpeta test_set
TEST_CASE_MAPPING = {
    "Kaqchikel_146": os.path.join("..", "test_set", "Gramatica-Normativa-Kaqchikel_páginas_146.xml"),
    "Kaqchikel_172": os.path.join("..", "test_set", "Gramatica-Normativa-Kaqchikel_páginas_172.xml"),
    "Kiche_43":      os.path.join("..", "test_set", "Gramatica-Normativa-Kiche_páginas_43.xml"),
    "Mam_80":        os.path.join("..", "test_set", "Gramatica-Normativa-Mam_páginas_80.xml")
}