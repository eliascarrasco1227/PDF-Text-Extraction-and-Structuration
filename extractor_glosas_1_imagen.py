from google import genai
from google.genai import types

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
    'Caption this image.'
]
)

print(response.text)