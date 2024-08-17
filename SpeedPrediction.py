import requests
import json
from moviepy.editor import *
import soundfile as sf
from EnvAPI import get_API
from transcription import transcribeAudio
from TextToSpeech import Speech
def FindSpeed():
    Speech(transcribeAudio(),get_API(),"test_video_AI.mp3")
    OrgFile = sf.SoundFile("test_video_AI.mp3")
    OrgSeconds = OrgFile.frames/OrgFile.samplerate
    VideoFileClip("test_video.mp4").audio.write_audiofile("test_video.mp3")
    ActualFile = sf.SoundFile("test_video.mp3")
    ActualSeconds = ActualFile.frames/ActualFile.samplerate
    print(OrgSeconds)
    print(ActualSeconds)
    return OrgSeconds / ActualSeconds
print(FindSpeed())