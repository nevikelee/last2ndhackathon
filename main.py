from flask import Flask, request, jsonify, render_template, flash, redirect, send_file
import requests
from flask_cors import CORS
import os
import boto3
import subprocess
import soundfile as sf
from moviepy.editor import *

API_KEY = "INSERT-TURBOLINE-API-HERE"

# Initialize flask and database
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './files'
app.config['SECRET_KEY'] = 'dnihawbdijawndiujhaw'
CORS(app)

# Check if uploaded file is video or audio
ALLOWED_EXTENSIONS = set(['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm'])
ALLOWED_AUDIO_EXTENSIONS = set(['flac', 'm4a', 'mp3', 'mpga', 'oga', 'ogg', 'wav', 'webm'])

# Checks if uploaded file is the correct format
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Determines whether a file has a supported audio format
def is_audio(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

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

# Find the speed of the tts audio so the audio and video are the same length
def FindSpeed(file, translated_text):
    video_filepath = f'./files/{file.filename}'
    audio_filepath = f'./files/temp_{file.filename}.mp3'
    Text_to_speech(audio_filepath, translated_text)
    OrgFile = sf.SoundFile(audio_filepath)
    OrgSeconds = OrgFile.frames/OrgFile.samplerate
    VideoFileClip(video_filepath).audio.write_audiofile(audio_filepath)
    ActualFile = sf.SoundFile(audio_filepath)
    ActualSeconds = ActualFile.frames/ActualFile.samplerate
    print(OrgSeconds)
    print(ActualSeconds)
    return OrgSeconds / ActualSeconds


# Text-to-speech method
def Text_to_speech(target_path, text, speed=1.0):
    url = "https://api.turboline.ai/openai/audio/speech"

    header = {
        "X-TL-Key" : API_KEY,
    }
    data = {
        "model": "tts-1",
        "input": text,
        "voice": "onyx",
        "response_format" : "mp3",
        "speed": speed
    }
    response = requests.post(url, headers=header, json=data, stream=True)
    
    if response.status_code == 200:
        try:
            os.remove(f"{target_path}")
        except OSError:
            pass
        if 'audio' in response.headers.get('Content-Type', ''):
            with open(f"{target_path}", 'wb') as f:
                f.write(response.content)
            print(f'Audio saved as {f"{target_path}"}')
        else:
            print("Unexpected content type received:", response.headers.get('Content-Type'))
            print("Response content:", response.text)
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Replaces an audio track of the video with an alternate audio and writes the result.
def Replace_sound(original_video_path, new_audio_path, destination_video_path):
    try:
        os.remove(destination_video_path)
    except OSError:
        pass
    try:
        command = [
            'ffmpeg',
            '-i', original_video_path,
            '-i', new_audio_path,
            '-c:v', 'copy',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            destination_video_path
        ]
        
        subprocess.run(command, check=True)
        print(f"Video sound replaced successfully. ")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
    except FileNotFoundError:
        print("ffmpeg is not installed or not found in the system PATH.")

# Main page
@app.route('/', methods=['GET', 'POST'])
def index():

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    
    if request.method == 'POST':

        file = request.files['video']
        language = request.form.get('languages')
        print(language)

        if(file and is_audio(file.filename)):
            # Saves uploaded file to files folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            
            flash(f'File {file.filename} has been uploaded')
            files = os.listdir(app.config['UPLOAD_FOLDER'])
            # Audio is transcribed and turned into text
            text_json = Transcribe(file.filename)
            text = text_json['text']

            # Text is translated into wanted language
            translated_text = TranslateText(text, language)

             # Translated text is turned into sound (Text-to-speech), audio file is saved
            Text_to_speech(f'./files/translated_{file.filename}', translated_text)

            return render_template('index.html', files=files, transcripted=text, translated=translated_text, download_name=f'translated_{file.filename}')
        elif file and allowed_file(file.filename):
            # Saves uploaded file to files folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            
            flash(f'File {file.filename} has been uploaded')
            files = os.listdir(app.config['UPLOAD_FOLDER'])
            # Audio is transcribed and turned into text
            text_json = Transcribe(file.filename)
            text = text_json['text']

            # Text is translated into wanted language
            translated_text = TranslateText(text, language)

            # Get the speed of the text
            speed = FindSpeed(file, translated_text)

            # Translated text is turned into sound (Text-to-speech), audio file is saved
            Text_to_speech(f'./files/translated_{file.filename}.mp3', translated_text, speed)

            # New speech replaces old speech in the original video
            Replace_sound(f'./files/{file.filename}', f'./files/{file.filename}.mp3', './files/translated_video.mp4')
            return render_template('index.html', files=files, transcripted=text, translated=translated_text, fileUrl='./files/translated_video.mp4')

        else:
            flash('Incorrect file type')
            redirect('/')
    return render_template('index.html', files=files)

# Download translated video
@app.route('/files/<filename>')
def get_file(filename):
    return send_file(os.path.join('files\\', filename), as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True)
