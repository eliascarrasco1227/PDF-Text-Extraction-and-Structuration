#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modificado para: Structured Output -> Salida XML
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from google import genai
from typing_extensions import TypedDict

# Configuración del cliente
model = 'gemini-3-flash-preview' # gemini-3-flash-preview también funciona
api_key = 'AIzaSyBiRpEOEHs5kr0xJ4a7elKPtf1C7qCXnro'
client = genai.Client(api_key=api_key)

# 1. Definimos el esquema (Structured Output)
# Esto obliga a la IA a ser 100% precisa con los datos
class Ingredient(TypedDict):
    amount_of_ingredient: float
    measure: str
    ingredient_name: str

class Recipe(TypedDict):
    recipe_name: str
    ingredients: list[Ingredient]

# 2. Configuración para Structured Output (JSON Schema)
config = {
    'response_mime_type': 'application/json',
    'response_schema': list[Recipe] # La API garantiza que los datos sigan este formato
}

prompt = """
Please extract the recipe from the following text.
The user wants to make delicious chocolate chip cookies.
They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,
1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,
3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.
For the best part, they'll need 2 cups of semisweet chocolate chips.
First, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,
baking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar
until light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry
ingredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons
onto ungreased baking sheets and bake for 9 to 11 minutes.
"""

# 3. Petición a la API
response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=config
)

# 4. Función para convertir el diccionario validado a XML
def json_to_xml(recipe_dict):
    root = ET.Element("recipe")
    
    # Nombre de la receta
    ET.SubElement(root, "recipe_name").text = recipe_dict['recipe_name']
    
    # Contenedor de ingredientes
    ingredients_node = ET.SubElement(root, "ingredients")
    
    for ing in recipe_dict['ingredients']:
        item = ET.SubElement(ingredients_node, "ingredient")
        ET.SubElement(item, "amount").text = str(ing['amount_of_ingredient'])
        ET.SubElement(item, "measure").text = ing['measure']
        ET.SubElement(item, "name").text = ing['ingredient_name']
    
    # Formateo "pretty print" para que el XML se vea bien
    xml_str = ET.tostring(root, encoding='utf-8')
    return minidom.parseString(xml_str).toprettyxml(indent="  ")

# 5. Iteramos sobre los resultados parseados y mostramos XML
# 'response.parsed' contiene los datos ya validados por el Structured Output
if response.parsed:
    for recipe_data in response.parsed:
        print(json_to_xml(recipe_data))






















        """
OUTPUT  

<?xml version="1.0" ?>
<recipe>
  <recipe_name>chocolate chip cookies</recipe_name>
  <ingredients>
    <ingredient>
      <amount>2.25</amount>
      <measure>cups</measure>
      <name>all-purpose flour</name>
    </ingredient>
    <ingredient>
      <amount>1.0</amount>
      <measure>teaspoon</measure>
      <name>baking soda</name>
    </ingredient>
    <ingredient>
      <amount>1.0</amount>
      <measure>teaspoon</measure>
      <name>salt</name>
    </ingredient>
    <ingredient>
      <amount>1.0</amount>
      <measure>cup</measure>
      <name>unsalted butter (softened)</name>
    </ingredient>
    <ingredient>
      <amount>0.75</amount>
      <measure>cup</measure>
      <name>granulated sugar</name>
    </ingredient>
    <ingredient>
      <amount>0.75</amount>
      <measure>cup</measure>
      <name>packed brown sugar</name>
    </ingredient>
    <ingredient>
      <amount>1.0</amount>
      <measure>teaspoon</measure>
      <name>vanilla extract</name>
    </ingredient>
    <ingredient>
      <amount>2.0</amount>
      <measure>large</measure>
      <name>eggs</name>
    </ingredient>
    <ingredient>
      <amount>2.0</amount>
      <measure>cups</measure>
      <name>semisweet chocolate chips</name>
    </ingredient>
  </ingredients>
</recipe>
        """