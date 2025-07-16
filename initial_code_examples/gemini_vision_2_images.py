from google import genai
from google.genai import types

client = genai.Client()

# Upload the first image
image1_path = "data/Gramatica-Normativa-Kiche_pag_40.pdf"
uploaded_file = client.files.upload(file=image1_path)

# Prepare the second image as inline data
image2_path = "data/Gramatica-Normativa-Kiche_pag_41.pdf"
with open(image2_path, 'rb') as f:
    img2_bytes = f.read()

# Create the prompt with text and multiple images
response = client.models.generate_content(

    model="gemini-2.5-flash",
    contents=[
        "What is different between these two images?",
        uploaded_file,  # Use the uploaded file reference
        types.Part.from_bytes(
            data=img2_bytes,
            mime_type='application/pdf'
        )
    ]
)

print(response.text)