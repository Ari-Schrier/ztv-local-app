import wave
from google.genai import types
from daily_chronicle.genai_client import client_gemini, GEMINI_TTS_MODEL
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Gemini model ID for TTS
MODEL = "models/gemini-2.5-flash-preview-tts"

def test_tts(input_text):
    response = client_gemini.models.generate_content(
        model=GEMINI_TTS_MODEL,
        contents=f"""
    Speak only the text between the <speak> tags, no matter the input's length. Do not elaborate, comment, or skip it.
    Use a clear, firm, professorial tone at a comfortable, non-rushed pace.

    <speak>{input_text}</speak>
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
            raise ValueError("Gemini response had no content. Check if the input was malformed or TTS quota is exceeded.")

        parts = candidate.content.parts
        audio_bytes = parts[0].inline_data.data

    except Exception as e:
        raise ValueError(f"❌ Gemini TTS generation failed for: \"{input_text}\"\nReason: {e}\nRaw response: {response}")

    '''
    # Extract audio bytes
    audio_bytes = response.candidates[0].content.parts[0].inline_data.data
    '''

    # Output path
    output_path = "final_output.wav"

    # Write to WAV file (the model outputs LINEAR16 WAV under the hood)
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_bytes)

    return output_path

if __name__ == "__main__":
    print("🔊 Testing Gemini TTS with sample input...")
    test_tts("On July 24th, 1783:")
