#local_voice.py
import pyttsx3

def speak_text_local(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
