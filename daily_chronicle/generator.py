# generator.py

# Core libs
import os
import json
import re
import time
from openai import OpenAI
import typing_extensions as typing
import numpy as np
from io import BytesIO

# Image handling
from PIL import Image

# Video + audio
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
import wave

# Async support (for potential async calls)
import asyncio
import contextlib

# Import client + model IDs
from daily_chronicle.genai_client import client, TEXT_MODEL, IMAGE_MODEL_ID

# Import prompt templates + types
from daily_chronicle.prompts import HistoricalEvent, EVENT_GENERATION_PROMPT_TEMPLATE

# Gemini
def generate_events_gemini(month: str, day: int, num_events: int = 3) -> list[HistoricalEvent]:
    prompt = EVENT_GENERATION_PROMPT_TEMPLATE.format(month=month, day=day, num_events=num_events)
    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': list[HistoricalEvent]
        }
    )
    try:
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Gemini event parsing failed: {e}")
        return []

# OpenAI
def generate_events_openai(month: str, day: int, num_events: int = 3) -> list[HistoricalEvent]:
    prompt = EVENT_GENERATION_PROMPT_TEMPLATE.format(month=month, day=day, num_events=num_events)
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.responses.create(
            model="gpt-4o",
            instructions="You are a historical event curator and pop culture/trivia for an educational slideshow for 4th graders.",
            input=prompt,
            temperature=0.3,
        )
        
        print(f"OpenAI response: {response.output_text}")

        # Extract JSON block from markdown-style code block
        json_match = re.search(r"```(?:json)?\s*(\[\s*{.*?}\s*])\s*```", response.output_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON block found in OpenAI response.")

        json_text = json_match.group(1)
        return json.loads(json_text)

    except Exception as e:
        print(f"❌ OpenAI event parsing failed: {e}")
        return []


# === Generate Events Function ===
def generate_events(month: str, day: int, num_events, event_generator_function) -> list[HistoricalEvent]:

    return event_generator_function(month, day, num_events)

if __name__ == "__main__":
    # Example usage
    month = "May"
    day = 14
    num_events = 3

    events = generate_events(month, day, num_events, generate_events_openai)
    if events:
        print(f"Generated {len(events)} events for {month} {day}:")
        for event in events:
            print(f"- {event.title} ({event.year})")
    else:
        print("No events generated.")