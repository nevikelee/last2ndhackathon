import requests
import json
from moviepy.editor import *
import soundfile as sf
from EnvAPI import get_API
from transcription import transcribeAudio
from TextToSpeech import Speech
def FindSpeed(filename,TTSfilename):
    Speech(transcribeAudio(),get_API(),TTSfilename)
    OrgFile = sf.SoundFile(TTSfilename)
    OrgSeconds = OrgFile.frames/OrgFile.samplerate
    VideoFileClip(filename).audio.write_audiofile("test_video.mp3")
    ActualFile = sf.SoundFile("test_video.mp3")
    ActualSeconds = ActualFile.frames/ActualFile.samplerate
    return OrgSeconds / ActualSeconds
