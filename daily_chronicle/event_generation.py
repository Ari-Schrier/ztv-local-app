# generator.py

import json

# Import client + model IDs
from daily_chronicle.genai_client import client_gemini, client_openai, GEMINI_TEXT_MODEL

# Import prompt templates + types
from daily_chronicle.prompts import HistoricalEvent, EVENT_GENERATION_PROMPT_TEMPLATE
from daily_chronicle.utils_logging import emoji

# JSON Schema equivalent of List[HistoricalEvent]
HISTORICAL_EVENT_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date_string": {"type": "string"},
                    "header_title": {"type": "string"},
                    "description": {"type": "string"},
                    "detail_1": {"type": "string"},
                    "detail_2": {"type": "string"},
                    "image_prompt": {"type": "string"},
                    "audio_text": {"type": "string"}
                },
                "required": [
                    "date_string",
                    "header_title",
                    "description",
                    "detail_1",
                    "detail_2",
                    "image_prompt",
                    "audio_text"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": ["events"],
    "additionalProperties": False
}

# Gemini
def generate_events_gemini(month: str, day: int, num_events: int = 3) -> list[HistoricalEvent]:
    prompt = EVENT_GENERATION_PROMPT_TEMPLATE.format(month=month, day=day, num_events=num_events)
    try:
        response = client_gemini.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': list[HistoricalEvent]
            }
        )
        return json.loads(response.text)

    except Exception as e:
        print(f"❌ Gemini event parsing failed: {e}")
        return []

# OpenAI
def generate_events_openai(month: str, day: int, num_events: int = 3) -> list[HistoricalEvent]:
    prompt = EVENT_GENERATION_PROMPT_TEMPLATE.format(month=month, day=day, num_events=num_events)
    try:
        response = client_openai.responses.create(
            model="gpt-4o",
            instructions="You are a historical event curator and pop culture/trivia expert for an educational slideshow for 4th graders.",
            input=prompt,
            temperature=0.3,
            text={ "format": { 
                "type": "json_schema", 
                "strict": True,
                "name": "HistoricalEventList",
                "schema": HISTORICAL_EVENT_LIST_SCHEMA,  } },
        )
        
        json_str = response.output_text
        parsed = json.loads(json_str)
        return parsed["events"]


    except Exception as e:
        print(f"❌ OpenAI event parsing failed: {e}")
        return []

# === Generate Events Function ===
def generate_events(month: str, day: int, num_events, event_generator_function) -> list[HistoricalEvent]:

    return event_generator_function(month, day, num_events)

def enhance_image_prompt(raw_prompt: str, logger=print) -> str:
    instructions = "You are an expert at writing detailed, vivid image generation prompts for AI art models."
    input = f"""Enhance the following prompt to make it more detailed, visual, and relevant for AI image generation.
                Especially consider the time period of the event, the cultural context, and any notable visual elements
                that would make the image more engaging for a 4th grade audience.
                Prompt: "{raw_prompt}"
                Enhanced prompt:"""

    try:

        response = client_openai.responses.create(
            model="gpt-4o",
            instructions=instructions,
            input=input,
            temperature=0.5
        )

        return response.output_text
    except Exception as e:
        logger(f"{emoji('cross_mark')} Failed to enhance image prompt: {e}")
        return raw_prompt

if __name__ == "__main__":
    # Example usage
    month = "May"
    day = 14
    num_events = 3

    print(generate_events(month, day, num_events, generate_events_openai))

    '''
    if events:
        print(f"Generated {len(events)} events for {month} {day}:")
        for event in events:
            print(f"- {event['header_title']} — {event['date_string']}")
    else:
        print("No events generated.")
    '''