from google import genai

# Initialize Gemini client
client = genai.Client(http_options={
    'api_version': 'v1alpha'
})

def list_available_models():
    for model in client.models.list():
        print(model.name)


# Model configs
TEXT_MODEL = "models/gemini-2.0-flash-exp"
IMAGE_MODEL_ID = "imagen-3.0-generate-002"
AUDIO_MODEL_ID = "models/gemini-2.5-flash-preview-tts"

def main():
    print("Available models:")
    list_available_models()
if __name__ == "__main__":
    main()