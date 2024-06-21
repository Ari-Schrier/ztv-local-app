from openai import OpenAI
import os
import json
from dotenv import load_dotenv, dotenv_values 
from openAI.prompting import jsonPreamble
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