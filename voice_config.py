# voice_config.py

# 🔽 Change to True to use gTTS (online voice), False for pyttsx3 (offline voice)
USE_ONLINE_VOICE = False  # Set to True if you want gTTS-based voice alerts

def speak_message(text):
    if USE_ONLINE_VOICE:
        from online_voice import speak_text_online
        speak_text_online(text)
    else:
        from offline_voice import speak_text_offline
        speak_text_offline(text)
