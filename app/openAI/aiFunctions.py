from openai import OpenAI
import os
import json
from dotenv import load_dotenv, dotenv_values 
from openAI.prompting import jsonPreamble, justThePics
load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def getJson(title):

    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": jsonPreamble},
        {"role": "user", "content": title}
    ]
    )

    data = completion.choices[0].message.content
    parsedData = json.loads(data)
    return parsedData

def getThePics(title):
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": justThePics},
        {"role": "user", "content": title}
    ]
    )

    data = completion.choices[0].message.content
    parsedData = json.loads(data)
    return parsedData

def getSpeech(filename, text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input= text
    )

    with open(filename, 'wb') as f:
        f.write(response.content)