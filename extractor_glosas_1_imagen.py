from google import genai
from google.genai import types
import os
from datetime import datetime

# Crear la carpeta output si no existe
os.makedirs('output', exist_ok=True)

client = genai.Client()

# Ruta del archivo PDF
pdf_path = 'data/Gramatica-Normativa-Kiche_PAG_20.pdf'
# Ruta del archivo de prompt
#prompt_path = 'prompts/prompt_v1'
prompt_path = 'prompts/prompt_v2'

# Leer el prompt
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt = f.read().strip()

#print(f"Prompt leído: {prompt}")

# Leer el PDF
with open(pdf_path, 'rb') as f:
    image_bytes = f.read()

# Generar la respuesta
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='application/pdf',
        ),
        prompt
    ]
)

# Mostrar respuesta en consola
print(response.text)

# Generar nombre de archivo único con timestamp
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# output_filename = f"output/respuesta_{timestamp}.txt"

# Alternativa con numeración secuencial
counter = 1
while os.path.exists(f"output/respuesta_{counter}.txt"):
    counter += 1
output_filename = f"output/respuesta_{counter}.txt"

# Guardar la respuesta en archivo
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"\nRespuesta guardada en: {output_filename}")