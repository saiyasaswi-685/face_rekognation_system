# offline_voice.py
import pyttsx3

def speak_text_offline(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)      # Speed of speech (you can change this if it's too fast/slow)
    engine.setProperty("volume", 1.0)    # Volume level (1.0 is max)
    engine.say(text)
    engine.runAndWait()
