from google import genai
from google.genai import types


# Ruta del archivo PDF
pdf_path = 'data/Gramatica-Normativa-Kiche_PAG_20.pdf'
# Ruta del archivo de texto que contiene el prompt
prompt_path = 'prompts/prompt_v1'  # Cambia esto por la ruta correcta

# Leer el prompt desde el archivo txt
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt = f.read().strip()  # strip() elimina espacios en blanco y saltos de línea al inicio y final

print (f"Prompt leído: {prompt}")

client = genai.Client()

path = 'data/Gramatica-Normativa-Kiche_PAG_20.pdf'

with open(path, 'rb') as f:
    image_bytes = f.read()

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

print(response.text)