
from EnvAPI import get_API
import requests
from transcription import transcribeAudio
from TextTranslations import TranslateText

def Speech(text, user_api_key, output_file):
    url = "https://api.turboline.ai/openai/audio/speech"

    header = {
        "X-TL-Key" : user_api_key,
    }
    data = {
        "model": "tts-1",
        "input": text,
        "voice": "onyx",
        "response_format" : "mp3"
    }
    response = requests.post(url, headers=header, json=data, stream=True)
    
    if response.status_code == 200:
        if 'audio' in response.headers.get('Content-Type', ''):
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"Audio saved as {output_file}")
        else:
            print("Unexpected content type received:", response.headers.get('Content-Type'))
            print("Response content:", response.text)
    else:
        print(f"Error: {response.status_code} - {response.text}")

api_key = get_API()  # Replace with your actual API key
text = TranslateText(transcribeAudio(), "Lithuanian")
output_file = "output_audio.mp3"

Speech(text, api_key, output_file)
