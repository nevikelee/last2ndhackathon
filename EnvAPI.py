from dotenv import load_dotenv
import os

def get_API():
    load_dotenv()
    return os.getenv("TURBOLINE_API_KEY") 