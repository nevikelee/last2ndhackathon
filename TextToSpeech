import boto3
import boto3.session
from transcription import transcribeAudio
from TextTranslations import TranslateText

session = boto3.Session(
    aws_access_key_id = "AKIAWOOXUE43YA7PZ7O6",
    aws_secret_access_key = "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",
    region_name = "eu-north-1"

)
polly = session.client('polly')

response = polly.synthesize_speech(
    Text=TranslateText(transcribeAudio()['text'],"Italian"),
    OutputFormat="mp3",
    VoiceId="Joanna",
    LanguageCode = "it-IT"
)
with open("testas.mp3",'wb') as file:
    file.write(response['AudioStream'].read())


    print("mp3 file saved")
