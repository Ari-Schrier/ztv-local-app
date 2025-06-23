# daily_chronicle/audio_generation.py

import os
import wave
import asyncio
import contextlib
from google import genai
import openai
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
# -- OLD FUNCTION -- needs to be rewritten if we want to use it
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
def generate_tts_gemini(narration_text: str, desired_filename: str) -> str:
    from google.genai import types
    
    response = client.models.generate_content(
        model=AUDIO_MODEL_ID,
        contents=f'''
        TTS the following text, speaking in a professorial, firm, and informative tone, at a comfortable, non-rushed pace, as a narrator for an educational video:
        {narration_text}
        ''',
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Orus',
                    )
                ),
            ),
        )
    )

    '''
    # Fallback guard
    try:
        parts = response.candidates[0].content.parts
    except (AttributeError, IndexError, TypeError):
        raise ValueError(f"❌ TTS generation failed for text: '{narration_text}'")
    '''
        
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

def generate_tts_openai(narration_text: str, desired_filename: str) -> str:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    instructions = """🎙️ Historical Event Curator – Voice Profile\n\nAffect:\nThoughtful and composed. Each word feels carefully chosen, as if revealing something meaningful. Speaks with quiet reverence for the past, inviting the listener to pause and reflect.\n\nTone:\nWarm, scholarly, and respectful. Never dry — always engaged. Holds a quiet passion for history, communicated through subtle inflection and sincerity.\n\nPacing:\nDeliberate and slow.\nAllows time for the listener to absorb each detail. Natural pauses after dates, names, or pivotal phrases help orient the listener in time and meaning. Never rushed.\n\nEmotions:\nCalm curiosity.\nA gentle sense of awe at the unfolding of history. Occasionally tinged with solemnity or admiration, depending on the gravity of the moment.\n\nPronunciation:\nClear and articulate.\nDates, places, and names are given special care. The delivery avoids contractions and slang, leaning into a formal but approachable style.\n\nPauses:\n\nAfter dates: to signal a historical moment.\n\nBefore an"""

    # Generate TTS using OpenAI's API
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="echo",  # Specify the voice configuration
        instructions = instructions,
        input=narration_text,
        response_format="wav",  # Specify the response format
    )

    # Save audio bytes directly
    output_path = os.path.join(TEMP_AUDIO_DIR, desired_filename)
    with open(output_path, "wb") as f:
        f.write(response.content)

    temp_audio_files.append(output_path)
    return output_path