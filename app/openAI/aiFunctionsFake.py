import json

def getJson(title):
    jsonString =  """[
      {
        "id": "slide1", 
        "title": ["Bee on Flower", "Abeja en Flor", "Abeille sur Fleur"], 
        "funFact": ["Bees are crucial for pollination of many plants.", "Las abejas son cruciales para la polinización de muchas plantas.", "Les abeilles sont cruciales pour la pollinisation de nombreuses plantes."], 
        "question": ["Have you ever seen a bee collecting nectar?", "¿Alguna vez has visto una abeja recolectar néctar?", "Avez-vous déjà vu une abeille récolter du nectar?"], 
        "prompt": "A close-up of a bee sitting on a colorful flower, collecting nectar, in a garden setting.", 
        "photo": "app/zbot.webp"
      },
      {
        "id": "slide2", 
        "title": ["Beehive", "Colmena", "Ruche"], 
        "funFact": ["Bees live in structured communities inside beehives.", "Las abejas viven en comunidades estructuradas dentro de colmenas.", "Les abeilles vivent en communautés structurées à lintérieur des ruches."], 
        "question": ["Do you remember seeing a beehive before?", "¿Recuerdas haber visto una colmena antes?", "Vous souvenez-vous avoir vu une ruche avant?"], 
        "prompt": "A medium shot of a beehive hanging from a tree branch, with bees entering and exiting.", 
        "photo": "app/bee.png"
      },
      {
        "id": "slide3", 
        "title": ["Honey Jar", "Tarro de Miel", "Pot de Miel"], 
        "funFact": ["Honey is the sweet product made by bees from flower nectar.", "La miel es el producto dulce que las abejas hacen del néctar de las flores.", "Le miel est le produit sucré fabriqué par les abeilles à partir de nectar de fleurs."], 
        "question": ["Do you like honey on your toast?", "¿Te gusta la miel en tu tostada?", "Aimez-vous le miel sur votre toast?"], 
        "prompt": "A close-up of a jar of honey with a wooden honey dipper beside it, placed on a rustic wooden table.", 
        "photo": "app/zbot.webp"
      }
    ]"""
    
    parsedData = json.loads(jsonString)
    return parsedData

print(getJson("blah"))