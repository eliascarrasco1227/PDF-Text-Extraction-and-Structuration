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
#HYPOTHESIS_XML = "../output/Gramatica-Normativa-Kaqchikel"


#HYPOTHESIS_XML = "../output/antiguos/13-pdf/Gramatica-Normativa-Kaqchikel"
#HYPOTHESIS_XML = "../output/2.5-flash/Gramatica-Normativa-Kaqchikel"

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43-43_version_1.xml"
#HYPOTHESIS_XML = "../output/7-pruebas_para_test_set_repetidas/few-shot-kiche/G"

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_172.xml"
#HYPOTHESIS_XML = "../output/9-doble_few_shot/Kaqchikel_146/G"

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43.xml"
#HYPOTHESIS_XML = "../output/9-doble_few_shot/Kiche/G"



#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_172.xml"
#HYPOTHESIS_XML = "../output/experiment_results/temp_0_0/Kaqchikel_172/G"

#REFERENCE_XML = "../test_set/Gramatica-Normativa-Kiche_páginas_43.xml"
#HYPOTHESIS_XML = "../output/Gramatica-Normativa-Kiche_pag_44_páginas_1-1_version_7.xml"

#REFERENCE_XML = "../test_set/Gramatica-Descriptiva-Qanjobal_pag_201.xml"
#HYPOTHESIS_XML = "../output/Gramatica-Descriptiva-Qanjobal"

REFERENCE_XML = "../test_set/Gramatica-Normativa-Kaqchikel_páginas_172.xml"
HYPOTHESIS_XML = "../output/experiment_results/gemini-3.1/temp_0/Gramatica-Normativa-Kaqchikel_pag_172"

import os

EXPERIMENTS_DIR = os.path.join("..", "output", "experiment_results", "gemini-3.1")

# ref: XML de referencia | prefix: prefijo exacto de los archivos de hipótesis
TEST_CASE_MAPPING = {
    "Kaqchikel_146": {
        "ref":    os.path.join("..", "test_set", "Gramatica-Normativa-Kaqchikel_páginas_146.xml"),
        "prefix": "Gramatica-Normativa-Kaqchikel_pag_146_"
    },
    "Kaqchikel_172": {
        "ref":    os.path.join("..", "test_set", "Gramatica-Normativa-Kaqchikel_páginas_172.xml"),
        "prefix": "Gramatica-Normativa-Kaqchikel_pag_172_"
    },
    "Kiche_43": {
        "ref":    os.path.join("..", "test_set", "Gramatica-Normativa-Kiche_páginas_43.xml"),
        "prefix": "Gramatica-Normativa-Kiche_pag_43_"
    },
    "Mam_80": {
        "ref":    os.path.join("..", "test_set", "Gramatica-Normativa-Mam_páginas_80.xml"),
        "prefix": "Gramatica-Normativa-Mam_pag_80_"
    },
}