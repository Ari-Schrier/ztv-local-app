import wikipediaapi
from openai import OpenAI
import os
import json
import base64
import requests
from dotenv import load_dotenv

summaryPreamble = "You are a helpful assistant that extracts fun facts from articles for easy comsumption."\
"Your summeries will be used as part of a 'today in history' presentation to be used at nursing homes. " \
"You will be given an article, a relevant date, and a brief explanation of why that date is relevant. "\
"You will condense the relevant information into two slides explaining the significance of the date to the article and providing background information."\
"You will avoid bringing in any outside knowledge not included in the presented article."\
"Your summary will be read out loud to dementia patients. Keep your vocabulary around a fourth-grade reading level. " \
"Less is often more with these summaries-- focus more on entertainment and less on completeness and technical detail. Each slide in your response should be no more than twenty words long." \
"Your response will be formatted as a JSON array and should look like this:"

summaryJsonDescription = """
[
  {
    "SlideOne": "A brief introduction to the subject-- make sure to highlight how it relates to the relevant date",
    "SlideTwo": "Another sentence or two sharing interesting information about the subject which may not be as closely tied to the date",
  },
]

ONLY SEND BACK THE JSON!!! This is very important. If you send back anything beyond the JSON, the system will crash.
"""

topicsPreamble = "You are a helpful assistant planning content for a presentation titled 'Today in History'."\
"You will be given a day, as well as the text of a wikipedia article on events that occured on that day. " \
"You will read the article and select twelve events which will be covered in the presentation. "\
"Your recommendations will be fed to another AI for summarization."\
"For each event you choose, include the title of the wikipedia which the next AI should summarize, as well as a short sentence on the relevance of the date to the subject."\
"Choose topics which will be relevant to senior citizens. Major historical events in the 19th centurys are good, but most events should be from the 20th century. Avoid events from the 18th or 21st centuries. Do not include any wars, disasters, deaths, or military actions." \
"Make sure that your selection includes at least one birthday of a relevant historical figure." \
"Keep chosen events as relevant to an audience of 21st century seniors as possible." \
"Your response will be formatted as a JSON array and should look like this:"

topicsJsonDescription = """
[
  {
    "summary": "A short sentence explaining the relationship between the subject and the date",
    "subject": "The subject of the event. If this is a historical figure, their name. If it's an event, the name of the event. This will later be used to guide the program to the correct wikipedia article, so DO NOT CHOOSE MULTIPLE SUBJECTS",
    "prompt": "a prompt which, if given to an image-generation model, could produce a reasonable illustration of the event."
  },
  {
  REPEAT FOR THE REMAINING ELEVEN EVENTS
  },
]

ONLY SEND BACK THE JSON!!! This is very important. If you send back anything beyond the JSON, the system will crash.

Try to keep the JSON in roughly chronological order
"""


def getJson(text, summary:bool):

    load_dotenv() 
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if summary:
        preamble = summaryPreamble + summaryJsonDescription
    else:
        preamble = topicsPreamble + topicsJsonDescription            
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

def saveJSON(fileName, text, summary):
    # Generate the JSON data
    myJson = getJson(text, summary)

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
        #instructions="You are reading aloud for dementia patients. Speak slowly and clearly.",
        input=text
    )

    with open(filename, 'wb') as f:
        f.write(response.content)
        
if __name__ == "__main__":
    load_dotenv() 
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='ZinniaTestAgent (schrier.a@northeastern.edu)', language='en')

    page = wiki_wiki.page("Emma Nutt")

    digestMe = (page.text)

    saveJSON(digestMe)