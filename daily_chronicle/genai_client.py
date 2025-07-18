import os
from google import genai
import openai

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Initialize Gemini client
client_gemini = genai.Client(http_options={
    'api_version': 'v1alpha'
})

# Initialize OpenAI client
client_openai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def list_available_models():
    for model in client_gemini.models.list():
        print(model.name)


# Model configs
GEMINI_TEXT_MODEL = "models/gemini-2.0-flash-exp"
GEMINI_IMG_MODEL = "imagen-3.0-generate-002"
GEMINI_TTS_MODEL = "models/gemini-2.5-flash-preview-tts"

def main():
    print("Available models:")
    list_available_models()
if __name__ == "__main__":
    main()