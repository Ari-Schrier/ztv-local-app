# daily_chronicle/audio_generation.py

from pathlib import Path
import wave
from google.genai import types
from daily_chronicle.genai_client import client_gemini, client_openai, GEMINI_TTS_MODEL
from daily_chronicle.slide_generation import temp_audio_files

# --- Temp storage directory setup ---
TEMP_AUDIO_DIR = Path(__file__).parent / "temp" / "temp_audio_files"
TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# --- Audio generation using Gemini TTS API ---
def generate_tts_gemini(narration_text: str, desired_filename: str) -> str:
    response = client_gemini.models.generate_content(
        model=GEMINI_TTS_MODEL,
        contents=f"""
        Speak only the text between the <speak> tags, no matter the input's
        length. Do not elaborate, comment, or skip it.
        Use a clear, firm, professorial tone at a comfortable,
        non-rushed pace.

        <speak>{narration_text}</speak>
        """,
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

    # --- Validate and extract audio ---
    try:
        candidate = response.candidates[0]
        if not candidate.content:
            raise ValueError("Gemini response had no content." \
            " Check if the input was malformed or TTS quota is exceeded.")

        parts = candidate.content.parts
        audio_bytes = parts[0].inline_data.data

    except Exception as e:
        raise ValueError(f"❌ Gemini TTS generation failed for: " \
                         f"\"{narration_text}\"\nReason: {e}\nRaw \
                         response: {response}")

    # Output path
    output_path = TEMP_AUDIO_DIR / desired_filename

    # Write to WAV file (the model outputs LINEAR16 WAV under the hood)
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_bytes)

    # Track temp file
    temp_audio_files.append(output_path)

    return output_path

def generate_tts_openai(narration_text: str, desired_filename: str) -> str:

    instructions = """
    🎙️ Historical Event Curator – Voice Profile\n\nAffect:\nThoughtful and composed. 
    Each word feels carefully chosen, as if revealing something meaningful. 
    Speaks with quiet reverence for the past, inviting the listener to pause and reflect.\n\n
    Tone:\nWarm, scholarly, and respectful. Never dry — always engaged. 
    Holds a quiet passion for history, communicated through subtle inflection and sincerity.\n\n
    Pacing:\nDeliberate and slow.\nAllows time for the listener to absorb each detail. 
    Natural pauses after dates, names, or pivotal phrases help orient the listener in time and meaning. 
    Never rushed.\n\n
    Emotions:\nCalm curiosity.\nA gentle sense of awe at the unfolding of history. 
    Occasionally tinged with solemnity or admiration, depending on the gravity of the moment.\n\n
    Pronunciation:\nClear and articulate.\nDates, places, and names are given special care. 
    The delivery avoids contractions and slang, leaning into a formal but approachable style.\n\n
    Pauses:\n\nAfter dates: to signal a historical moment.\n\n
    Before significant names or events — to create space for impact.\n\nBetween sentences — to allow for reflection"""

    # Generate TTS using OpenAI's API
    response = client_openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="echo",  # Specify the voice configuration
        instructions = instructions,
        input=narration_text,
        response_format="wav",  # Specify the response format
    )

    # Save audio bytes directly
    output_path = TEMP_AUDIO_DIR / desired_filename
    with output_path.open("wb") as f:
        f.write(response.content)

    temp_audio_files.append(str(output_path))
    return str(output_path)

def generate_event_audio(event, index, generate_tts_function, logger=print):
    clip1_toptext = f"{event['date_string']}"
    clip1_centertext = f"{event['description']} {event['detail_1']}"
    clip1_bottomtext = event["detail_2"]

    logger(f"🎙️ Generating TTS: \"{clip1_toptext}\"")
    audio_path_1 = generate_tts_function(clip1_toptext, f"audio_{index + 1}_toptext.wav")
    logger(f"🎙️ Generating TTS: \"{clip1_centertext}\"")
    audio_path_2 = generate_tts_function(clip1_centertext, f"audio_{index + 1}_centertext.wav")
    logger(f"🎙️ Generating TTS: \"{clip1_bottomtext}\"")
    audio_path_3 = generate_tts_function(clip1_bottomtext, f"audio_{index + 1}_bottomtext.wav")
    temp_audio_files.extend([audio_path_1, audio_path_2, audio_path_3])

    logger(f"✅ TTS saved: {str(audio_path_1)}")
    logger(f"✅ TTS saved: {str(audio_path_2)}")
    logger(f"✅ TTS saved: {str(audio_path_3)}")

    return audio_path_1, audio_path_2, audio_path_3