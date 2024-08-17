from flask import Flask, request, jsonify, render_template, flash, redirect
import requests
from flask_cors import CORS
import os

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
def transcribe(filename):
    url = 'https://api.turboline.ai/openai/audio/transcriptions'

    header = {
        "X-TL-Key" : "9fb2c952d7ef4badb5c3b9c60bac8f78"
    }

    data = {
        "model" : "whisper-1",
        "prompt" : "transcribe this audio into text",
        "language" : "en",
        "response_format" : "verbose_json",
        "timestamp_granularities" : ["word"]
    }

    files = {"file":  open(f'./files/{filename}', "rb")}

    response = requests.post(url, headers=header, data=data, files=files)
    # for timestamp in response.json()['segments']:
    #     # print(str(round(timestamp['start'], 2)) + ' - ' + str(round(timestamp['end'], 2)) + ': ' + timestamp['text'])
    #     print(timestamp)

    return response.json()

# Main page
@app.route('/', methods=['GET', 'POST'])
def index():
    
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    print(files)

    if request.method == 'POST':

        file = request.files['video']

        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

            text = transcribe(file.filename)
            
            flash(f'File {file.filename} has been uploaded')
            files = os.listdir(app.config['UPLOAD_FOLDER'])

            return render_template('index.html', files=files, transcripted=text['text'])
        else:
            flash('Incorrect file type')
            redirect('/')
    

    return render_template('index.html', files=files)

if __name__ == "__main__":
    app.run(debug=True)