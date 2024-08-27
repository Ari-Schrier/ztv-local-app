import requests
import os
from dotenv import load_dotenv
OUTPUT_DIRECTORY = "output"


# def makeImage(fileName, prompt):
#     load_dotenv() 
#     myKey = os.getenv("STABILITY_API_KEY")

#     response = requests.post(
#         f"https://api.stability.ai/v2beta/stable-image/generate/core",
#         headers={
#             "authorization": myKey,
#             "accept": "image/*"
#         },
#         files={"none": ''},
#         data={
#             "prompt": prompt,
#             "output_format": "webp",
#         },
#     )

#     if response.status_code == 200:
#         with open(f"./{fileName}.webp", 'wb') as file:
#             file.write(response.content)
#     else:
#         raise Exception(str(response.json()))

# def getImage(title, myJson):
#     load_dotenv() 
#     myKey = os.getenv("STABILITY_API_KEY")
#     if not os.path.exists(OUTPUT_DIRECTORY):
#         os.makedirs(OUTPUT_DIRECTORY)
    
#     new_folder_path = os.path.join(OUTPUT_DIRECTORY, title)

#     if not os.path.exists(new_folder_path):
#         os.makedirs(new_folder_path)


#     for element in myJson:
#         print(f"Processing {element["id"]:}")
#         print(f"Generating {element["prompt"]}")
#         element["photo"] = f"{OUTPUT_DIRECTORY}/{title}/{element["id"]}.png"
#         response = requests.post(
#         f"https://api.stability.ai/v2beta/stable-image/generate/core",
#         headers={
#             "authorization": myKey,
#             "accept": "image/*"
#         },
#         files={"none": ''},
#         data={
#             "prompt": element["prompt"],
#             "output_format": "png",
#             "aspect_ratio": "16:9",
#             "style_preset": "photographic"
#         },
#         )

#         if response.status_code == 200:
#             with open(f"{new_folder_path}\\{element["id"]}.png", 'wb') as file:
#                 file.write(response.content)
#         else:
#             raise Exception(str(response.json()))
#     return myJson

def getPathToImage(title, prompt, id, ratio="16:9"):
    load_dotenv() 
    myKey = os.getenv("STABILITY_API_KEY")
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    
    new_folder_path = os.path.join(OUTPUT_DIRECTORY, title)

    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    f"{OUTPUT_DIRECTORY}/{title}/{id}.png"
    response = requests.post(
    f"https://api.stability.ai/v2beta/stable-image/generate/core",
    headers={
        "authorization": myKey,
        "accept": "image/*"
    },
    files={"none": ''},
    data={
        "prompt": prompt,
        "output_format": "png",
        "aspect_ratio": ratio,
        "style_preset": "photographic"
    },
    )

    if response.status_code == 200:
        with open(f"{new_folder_path}\\{id}.png", 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(str(response.json()))
    return f"{OUTPUT_DIRECTORY}/{title}/{id}.png"

