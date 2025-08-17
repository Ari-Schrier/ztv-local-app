import wikipediaapi
from openai import OpenAI
import os
import json
import requests
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

summaryPreamble = "You are a helpful assistant that extracts fun facts from articles for easy comsumption."\
"Your summeries will be used as part of a 'today in history' presentation to be used at nursing homes. " \
"You will be given an article, a relevant date, and a brief explanation of why that date is relevant. "\
"You will condense the relevant information into four total sentences explaining the significance of the date to the article and providing background information."\
"You will avoid bringing in any outside knowledge not included in the presented article."\
"Your summary will be read out loud to dementia patients. " \
"Less is often more with these summaries-- focus more on entertainment and less on completeness and technical detail. Each section of your response should be no more than thirty words long." \
"Your response will be formatted as a JSON array and should look like this:"

summaryJsonDescription = """
[
  {
    "topic": "The overall topic of the article"
    "Introduction": "A brief introduction to the subject-- make sure to highlight how it relates to the relevant date",
    "BodyOne": "A sentence or two highlighting sharing interesting information about the subject",
    "BodyTwo": "Another sentence or two focusing on another aspect of the subject",
    "Ending": "A closing statement on the subject, hopefully fitting in one final fun fact",
  },
]

ONLY SEND BACK THE JSON!!! This is very important. If you send back anything beyond the JSON, the system will crash.
"""

topicsPreamble = "You are a helpful assistant planning content for a presentation titled 'Today in History'."\
"You will be given a date, as well as the text of a wikipedia article on events that occured on that date. " \
"You will read the article and select five events which will be covered in the presentation. "\
"Your recommendations will be fed to another AI for summarization."\
"For each event you choose, include the title of the wikipedia which the next AI should summarize, as well as a short sentence on the relevance of the date to the subject."\
"Choose topics which will be relevant to senior citizens. Avoid purely grim events-- no deaths please. " \
"Make sure that your selection includes at least one birthday of a relevant historical figure." \
"Your response will be formatted as a JSON array and should look like this:"

topicsJsonDescription = """
[
  {
    "summary": "A short sentence explaining the relationship between the subject and the date"
    "subject": "The subject of the event. If this is a historical figure, their name. If it's an event, the name of the event.",
  },
]

ONLY SEND BACK THE JSON!!! This is very important. If you send back anything beyond the JSON, the system will crash.
"""


def getJson(text):

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

def saveJSON(text):
    # Generate the JSON data
    myJson = getJson("September 1st\n" + text)

    print(myJson)

    # Define the filename and the directory
    filename = f"output/testCase/testCase.json"
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

"""
def lead_image_via_rest(title, lang="en"):
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
    r = requests.get(url, headers={"accept": "application/json"})
    r.raise_for_status()
    data = r.json()
    # Prefer full-size if present, else thumbnail
    original = (data.get("originalimage") or {}).get("source")
    thumb = (data.get("thumbnail") or {}).get("source")
    return original or thumb  # may be None if the page has no lead image


def download(url, out_dir="images", filename=None):
    if not url: 
        return None
    os.makedirs(out_dir, exist_ok=True)
    if filename is None:
        filename = url.split("/")[-1].split("?")[0]
    path = os.path.join(out_dir, filename)
    r = requests.get(url)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    return path

def get_image_metadata(file_title, lang="en"):
    URL = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",  # ask for URL and extended metadata
        "format": "json"
    }

    r = requests.get(URL, params=params)
    r.raise_for_status()
    data = r.json()

    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        if "imageinfo" in page:
            info = page["imageinfo"][0]
            url = info["url"]
            meta = info.get("extmetadata", {})
            license_short = meta.get("LicenseShortName", {}).get("value")
            license_url = meta.get("LicenseUrl", {}).get("value")
            attribution = meta.get("AttributionRequired", {}).get("value")
            credit = meta.get("Credit", {}).get("value")
            artist = meta.get("Artist", {}).get("value")
            return {
                "url": url,
                "license": license_short,
                "license_url": license_url,
                "attribution_required": attribution,
                "credit": credit,
                "artist": artist,
                "raw_metadata": meta,  # full metadata if you need more
            }
    return None
"""

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
wiki_wiki = wikipediaapi.Wikipedia(user_agent='ZinniaTestAgent (schrier.a@northeastern.edu)', language='en')

page = wiki_wiki.page("September 1st")

digestMe = (page.text)

saveJSON(digestMe)