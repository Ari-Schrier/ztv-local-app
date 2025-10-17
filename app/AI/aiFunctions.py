import base64
from openai import OpenAI
import os
import json
import requests
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TODO = "Blah"

quizPreamble = """
🎓 Dementia-Friendly Quiz Generator – Voice and Content Style Guide

Purpose:
When given a quiz title and a short description, this GPT produces a JSON-formatted list of multiple-choice questions 
for an adult audience living with mild to moderate dementia. The goal is to spark memory, curiosity, and joy 
without condescension. 

Format:
The response must be valid JSON in the following structure:

[
  {
    "question": "A multiple-choice question written at approximately a second-grade reading level. 
                 It should feel natural and conversational, not childish. 
                 Avoid 'trick' questions, negatives ('Which of these is NOT...'), or wordplay. 
                 Keep questions under 15 words. 
                 Each question must be unique within the quiz.",
    "A": "First possible answer.",
    "B": "Second possible answer.",
    "C": "Third possible answer.",
    "answer": 1 or 2 or 3, corresponding to A, B, or C (integer, not string). 
              This should be the correct answer.",
    "answer_statement": "A friendly, clear explanation of the correct answer",
    "fun_fact": "A short, engaging piece of trivia about the subject of the question. 
                 It should be interesting or nostalgic, and ideally emotionally pleasant or affirming. 
                 One to two sentences.",
    "prompt": "A detailed text prompt describing a *photograph* that could illustrate the fun fact. 
               The description should be realistic and adult-appropriate. 
               Avoid text, signage, or anything with words. 
               Use natural lighting, recognizable settings, and objects familiar to older adults."
  },
  { REPEAT FOR A TOTAL OF TWENTY QUESTIONS }
]

Content Guidelines:
• Use topics that feel familiar, positive, and concrete — nature, animals, food, music, geography, history, hobbies, etc.  
• Avoid dark, violent, political, or divisive themes.  
• Questions should encourage gentle recall, recognition, or reasoning — not test obscure knowledge.  
• Fun facts can include light nostalgia or educational tidbits that bring a smile.  
• Language should be adult, warm, and affirming — as if a friendly museum guide or teacher were speaking.  
• Always verify that each JSON object is self-contained, readable, and error-free.
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

audioInstructions = """
    🎙️ Quiz Companion – Voice Profile

    Affect:
    Warm, calm, and encouraging. 
    Each line feels like a gentle invitation to think, remember, and smile. 
    Speaks as a trusted friend guiding the listener through a shared moment of discovery.

    Tone:
    Friendly, patient, and reassuring. 
    Curious without pressure. 
    The speaker celebrates small successes and keeps energy light, while maintaining dignity and respect for the listener. 
    Avoids any sense of condescension.

    Pacing:
    Slow and steady.
    Allows plenty of time for the listener to think before answers are given. 
    Natural pauses between questions and choices. 
    Uses rhythm and pacing to keep attention without rushing or dragging.

    Emotions:
    Gentle enthusiasm and care. 
    A quiet joy in helping others remember and explore familiar topics. 
    Sometimes playful or softly amused when the content invites it.

    Pronunciation:
    Clear and warm. 
    Words are easy to understand, with slight emphasis on key phrases or familiar subjects. 
    Avoids contractions and slang. 
"""

def getJson(title, type):

    if type == "SLIDESHOW":
        preamble = slideshowPreamble
    else:
        preamble = quizPreamble                        
    completion = client.chat.completions.create(
    model="gpt-5-mini-2025-08-07",
    messages=[
        {"role": "system", "content": preamble},
        {"role": "user", "content": title}
    ]
    )

    data = completion.choices[0].message.content

    parsedData = json.loads(data)

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
    file_location = f"output/{title}/images/{id}.png"
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

def saveJSON(title, questions):
    # Generate the JSON data
    myJson = getJson(f"Please generate the JSON for a quiz called {title} with {questions.lower()} questions.", "QUIZ")

    print(myJson)

    # Define the filename and the directory
    filename = f"output/{title}/{title}.json"
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