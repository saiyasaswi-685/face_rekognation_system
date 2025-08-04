# online_voice.py
from gtts import gTTS
import os

def speak_text_online(text):
    tts = gTTS(text=text, lang='en')
    tts.save("temp_audio.mp3")
    os.system("start temp_audio.mp3")  # On Windows

    # For Linux use:
    # os.system("mpg123 temp_audio.mp3")

    # Optionally, you can remove the file after playing
    # os.remove("temp_audio.mp3")
