from flask import Flask, request, jsonify, render_template, flash, redirect
import requests
from flask_cors import CORS
import os
import boto3

API_KEY = "9fb2c952d7ef4badb5c3b9c60bac8f78"

# Initialize flask and database
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './files'
app.config['SECRET_KEY'] = 'dnihawbdijawndiujhaw'
CORS(app)

# Check if uploaded file is video or audio
ALLOWED_EXTENSIONS = set(['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Transcription method
def Transcribe(filename):
    url = 'https://api.turboline.ai/openai/audio/transcriptions'

    header = {
        "X-TL-Key" : API_KEY
    }

    data = {
        "model" : "whisper-1",
        "prompt" : "transcribe this audio into text",
        "language" : "en"
    }

    files = {"file":  open(f'./files/{filename}', "rb")}

    response = requests.post(url, headers=header, data=data, files=files)

    return response.json()

# Translation method
def TranslateText(text, language):
    url = 'https://api.turboline.ai/openai/chat/completions'

    header = {
        "X-TL-Key" : API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages":[
             {"role": "system", "content": "You are a helpful assistant. Respond only with the translation."},
            {"role": "user", "content": f"Can you translate this into this language {language}: {text}"}
        ]
    }
    response = requests.post(url, headers=header, json=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content'].strip()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Text-to-speech method
def Text_to_speech(first_file, translated_text):
    print(translated_text)
    session = boto3.Session(
    aws_access_key_id = "AKIAWOOXUE43YA7PZ7O6",
    aws_secret_access_key = "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",
    region_name = "eu-north-1"
    )

    polly = session.client('polly')

    response = polly.synthesize_speech(
    Text=TranslateText(translated_text,"Lithuanian"),
    OutputFormat="mp3",
    VoiceId="Joanna",
    LanguageCode = "it-IT"
    )

    with open(f"./files/{first_file.filename}.mp3",'wb') as file:
        file.write(response['AudioStream'].read())

# Main page
@app.route('/', methods=['GET', 'POST'])
def index():
    language = 'Lithuanian'
    if request.method == 'POST':
        file = request.files['video']

        if file and allowed_file(file.filename):
            # Saves uploaded file to files folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            
            flash(f'File {file.filename} has been uploaded')

            # Audio is transcribed and turned into text
            text_json = Transcribe(file.filename)
            text = text_json['text']

            # Text is translated into wanted language
            translated_text = TranslateText(text, language)

            # Translated text is turned into sound (Text-to-speech), audio file is saved
            Text_to_speech(file, translated_text)

            return translated_text
        else:
            flash('Incorrect file type')
            redirect('/')
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)