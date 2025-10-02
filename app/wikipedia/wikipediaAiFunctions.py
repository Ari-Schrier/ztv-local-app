import wikipediaapi
from openai import OpenAI
import os
import json
import base64
import requests
from dotenv import load_dotenv
from prompts import updatedPrompt, audioInstructions


def getJson(text):

    load_dotenv() 
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    
    preamble = updatedPrompt          
    completion = client.chat.completions.create(
    model="gpt-5-mini-2025-08-07",
    messages=[
        {"role": "system", "content": preamble},
        {"role": "user", "content": text}
    ]
    )

    data = completion.choices[0].message.content

    parsedData = json.loads(data)

    return parsedData

def get_images_from_page(title, lang="en"):
    S = requests.Session()
    URL = f"https://{lang}.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "query",
        "titles": title,
        "prop": "images",
        "format": "json",
        "imlimit": "max"
    }

    R = S.get(url=URL, params=PARAMS)
    data = R.json()

    images = []
    pages = data.get("query", {}).get("pages", {})
    for pageid, page in pages.items():
        if "images" in page:
            for img in page["images"]:
                images.append(img["title"])
    return images

def get_image_urls(file_titles, lang="en"):
    S = requests.Session()
    URL = f"https://{lang}.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "query",
        "titles": "|".join(file_titles),
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }

    R = S.get(url=URL, params=PARAMS)
    data = R.json()

    urls = []
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        if "imageinfo" in page:
            urls.append(page["imageinfo"][0]["url"])
    return urls

def generatePicture(prompt, location):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="1024x1024",
    )
    
    image_base64 = response.data[0].b64_json
    image_data = base64.b64decode(image_base64)
    
    with open(location, "wb") as file:
        file.write(image_data)

def saveJSON(fileName, text):
    # Generate the JSON data
    myJson = getJson(text)

    print(myJson)

    # Define the filename and the directory
    filename = fileName
    directory = os.path.dirname(filename)

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Write the JSON data to the file
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(myJson, file, indent=4, ensure_ascii=False)
        print(f"File {filename} written successfully.")
    except Exception as e:
        print(f"Error writing file: {e}")

def getSpeech(filename, text, voice="echo"):
    load_dotenv() 
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        instructions=audioInstructions,
        input=text
    )

    with open(filename, 'wb') as f:
        f.write(response.content)

def getRelevantDataForDate(date):

    text=f"Please use the following wikipedia article, covering events on {date}:\n"
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='ZinniaTestAgent (schrier.a@northeastern.edu)', language='en')

    page = wiki_wiki.page(date)

    for section in page.sections:
        if section.title in ["Deaths", "References", "External links", "Holidays and Observences"]:
            continue
        if len(section.sections) == 0:
            text += "\n" + section.full_text()
        else:
            text += "\n" + section.title
            for sub in section.sections:
                if sub.title == "1901–present":
                    text += "\n" + sub.full_text()
    return text

        
if __name__ == "__main__":
    load_dotenv() 
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='ZinniaTestAgent (schrier.a@northeastern.edu)', language='en')

    page = wiki_wiki.page("August 26")

    text="Please use the following wikipedia article, covering events on August 26:\n"

    for section in page.sections:
        if section.title in ["Deaths", "References", "External links", "Holidays and Observences"]:
            continue
        if len(section.sections) == 0:
            text += "\n" + section.full_text()
        else:
            text += "\n" + section.title
            for sub in section.sections:
                if sub.title == "1901–present":
                    text += "\n" + sub.full_text()

    saveJSON("app/wikipedia/output/testCase/testjson.json", text)