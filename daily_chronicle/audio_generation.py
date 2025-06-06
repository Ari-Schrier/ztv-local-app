# daily_chronicle/audio_generation.py

import os
import wave
import asyncio
import contextlib
from google import genai
from daily_chronicle.genai_client import client, TEXT_MODEL, IMAGE_MODEL_ID, AUDIO_MODEL_ID

# --- Temp storage directory setup ---
TEMP_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "temp", "temp_audio_files")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# --- In-memory tracking for cleanup ---
temp_audio_files = []

# --- Wave file context manager ---
@contextlib.contextmanager
def wave_file(filename, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        yield wf

# --- Audio generation using Live API ---
def generate_audio_live(narration_text: str, desired_filename: str) -> str:
    collected_audio = bytearray()

    full_prompt = (
        "You are a voiceover narrator for an educational video. "
        "Do not comment, react, or summarize. "
        "Do not add introductions or conclusions. "
        "Do not ask questions. "
        "Just read the following text exactly, with a calm and clear tone:\n\n"
        f"{narration_text}"
    )

    async def _generate():
        config = {
            "response_modalities": ["AUDIO"]
        }
        async with client.aio.live.connect(model=TEXT_MODEL, config=config) as session:
            await session.send(input=full_prompt, end_of_turn=True)
            async for response in session.receive():
                if response.data:
                    collected_audio.extend(response.data)
        return bytes(collected_audio)

    # Run the async generator
    try:
        audio_bytes = asyncio.run(_generate())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        audio_bytes = loop.run_until_complete(_generate())

    # Output path in temp_audio
    output_path = os.path.join(TEMP_AUDIO_DIR, desired_filename)

    # Write to .wav file
    with wave_file(output_path) as wf:
        wf.writeframes(audio_bytes)

    # Track temp file
    temp_audio_files.append(output_path)

    return output_path

# --- Audio generation using Gemini TTS API ---
def generate_audio_tts(narration_text: str, desired_filename: str) -> str:
    from google.genai import types

    # Speech generation using generate_content()
    # Model: models/gemini-2.5-flash-preview-tts or models/gemini-2.5-pro-preview-tts
    
    response = client.models.generate_content(
        model=AUDIO_MODEL_ID,  # e.g. "models/gemini-2.5-flash-preview-tts"
        contents=narration_text,  # Now pass string directly, not [{"role": ..., "parts": ...}]
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',  # You can change this later if you want
                    )
                ),
            ),
        )
    )
    
    # Extract audio bytes
    audio_bytes = response.candidates[0].content.parts[0].inline_data.data
    
    # Output path
    output_path = os.path.join(TEMP_AUDIO_DIR, desired_filename)

    # Write to WAV file (the model outputs LINEAR16 WAV under the hood)
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_bytes)

    # Track temp file
    temp_audio_files.append(output_path)

    return output_path
