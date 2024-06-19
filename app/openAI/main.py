import json
from aiFunctions import getJson

json_string=getJson("All About Ptarmigans!")

print(json_string)

parsed_data = json.loads(json_string)

# Print the parsed data to verify
for slide in parsed_data:
    print(f"ID: {slide['id']}")
    print(f"Title: {slide['title'][0]}")
    print(f"Fun Fact: {slide['funFact'][0]}")
    print(f"Question: {slide['question'][0]}")
    print(f"Prompt: {slide['prompt']}\n")