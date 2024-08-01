from openai import OpenAI
import os
import json
from dotenv import load_dotenv, dotenv_values 
from preambles import jsonPreamble
load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TODO = "Blah"

def getJson(title):

    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": jsonPreamble},
        {"role": "user", "content": title}
    ]
    )

    data = completion.choices[0].message.content

    print(data)
    parsedData = json.loads(data)
    return parsedData

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

def getSpeech(filename, text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input= text
    )

    with open(filename, 'wb') as f:
        f.write(response.content)
def saveJSON(title, questions):
    # Generate the JSON data
    myJson = getJson(f"Please generate the JSON for a quiz called {title} with {questions.lower()} questions.")

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
