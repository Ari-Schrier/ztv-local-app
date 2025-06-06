# generator.py

# Core libs
import os
import json
import time
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


# === Generate Events Function ===
def generate_event_sequence(month: str, day: int, num_events: int = 3) -> list[HistoricalEvent]:
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
        event_data = json.loads(response.text)
        if isinstance(event_data, list) and len(event_data) > 0:
            return event_data
        else:
            print("⚠️ No valid event data returned.")
            return []
    except (KeyError, TypeError, IndexError, json.JSONDecodeError) as e:
        print(f"❌ Error parsing JSON: {e}")
        return []
