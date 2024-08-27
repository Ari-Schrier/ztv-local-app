from openai import OpenAI
import os
import json
import requests
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TODO = "Blah"

quizPreamble = """I'm building a program to present quizzes to viewers. I would like you to make a sample quiz for me. I would like your response in a JSON formatted as follows:

[
{
"id": "a unique ID for this question",
"question":"A multiple-choice question at about a second-grade difficulty level",
"A":"A) a potential answer",
"B":"B) a potential answer",
"C":"C) a potential answer",
"D":"D) a potential answer",
"answer":"A, B, C, or D",
"fun fact":"A short piece of trivia about the subject of the question"
"prompt":"Give a brief description which could be used with an AI image-generation model to generate a photograph illustrating the fun fact. 
The prompt should be very simple-- simply state the subject, the background, and what the subject is doing.
Do not include any text, and be very specific with the number of objects present in the photograph.
Also include mention of the type of camera used to take the photograph, and what sort of lens was used with it."
},
{REPEAT FOR ALL QUESTIONS}
]

ONLY SEND BACK THE JSON!!! This is very important. If you send back anything beyond the JSON, the system will crash.
"""

slideshowPreamble = """You are a helpful assistant who assists users in brainstorming slideshows to be shown to dementia patients. When you are given a title for a slideshow, you suggest a set of slides which might be put in a slideshow with that title. These slideshows are intended to be viewed by dementia patients. All slides should be nostalgic and non-threatening. Avoid any subjects which might frighten a viewer. Most slides should not focus on humans. Your response will be formatted as a JSON array and should look like this:

[
  {
    "id": "A unique identifier for the slide"
    "title": "title of slide. Should be short and descriptive",
    "funFact": "a brief interesting fact about the subject of the slide",
    "prompt": "A  prompt which could be used with an AI image-generation model to create a photograph illustrating the slide. Try to avoid difficult topics to generate, like hands and text. Possibly include a photography-specific word. (for example, for a portrait of a specific subject you might mention bokeh)"
  },
  {Repeat for all slides}
]

ONLY SEND BACK THE JSON!!! This is very important. If you send back anything beyond the JSON, the system will crash.
"""



def getJson(title, type):

    if type == "SLIDESHOW":
        preamble = slideshowPreamble
    else:
        preamble = quizPreamble                        
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": preamble},
        {"role": "user", "content": title}
    ]
    )

    data = completion.choices[0].message.content

    parsedData = json.loads(data)

    for each in parsedData:
        each["image_path"] = "resources/default_image.png"
    return parsedData


def getPictureURL(title, prompt, id):
    begging = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"{begging} {prompt}",
        n=1,
        size="1792x1024",
        style="natural"
        )
    image_url = response.data[0].url
    image_data = requests.get(image_url).content
    file_location = f"output/{title}/{id}.png"
    with open(file_location, "wb") as file:
        file.write(image_data)
    return file_location

def getThePics(title):
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": TODO},
        {"role": "user", "content": title}
    ]
    )

    data = completion.choices[0].message.content
    parsedData = json.loads(data)
    return parsedData

def getSpeech(filename, text, voice="echo"):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input= text
    )

    with open(filename, 'wb') as f:
        f.write(response.content)
def saveJSON(title, questions, type):
    # Generate the JSON data
    myJson = getJson(f"Please generate the JSON for a quiz called {title} with {questions.lower()} questions.", type)

    # Define the filename and the directory
    filename = f"output/{title}/{title}.json"
    directory = os.path.dirname(filename)

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Write the JSON data to the file
    try:
        with open(filename, "w") as file:
            json.dump(myJson, file, indent=4)
        print(f"File {filename} written successfully.")
    except Exception as e:
        print(f"Error writing file: {e}")