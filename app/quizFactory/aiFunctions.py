from openai import OpenAI
import os
import json
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TODO = "Blah"

jsonPreamble = """I'm building a program to present quizzes to viewers. I would like you to make a sample quiz for me. I would like your response in a JSON formatted as follows:

[
{
"question":"A multiple-choice question at about a second-grade difficulty level",
"A":"A) a potential answer",
"B":"B) a potential answer",
"C":"C) a potential answer",
"D":"D) a potential answer",
"answer":"A, B, C, or D",
"fun fact":"A short piece of trivia about the subject of the question"
"prompt":"Give a brief description which could be used with an AI image-generation model to generate a photograph illustrating the fun fact. 
The prompt should be very simple-- simply state the subject, the background, and what the subject is doing.
Do not include any words, and be very specific with the number of objects present in the photograph.
Also include mention of the type of camera used to take the photograph, and what sort of lens was used with it."
},
{REPEAT FOR ALL QUESTIONS}
]

ONLY SEND BACK THE JSON!!! This is very important. If you send back anything beyond the JSON, the system will crash.
"""


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

    for each in parsedData:
        each["image_path"] = "resources/default_image.png"
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

if __name__ == "__main__":
    with open("output/WhaleQuiz/WhaleQuiz.json", "r") as file:
        whales = json.load(file)
    for each in whales:
        print(each)