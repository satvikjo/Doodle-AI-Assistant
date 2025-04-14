import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    engine.setProperty('volume', 1.0)

    # Set to preferred voice — e.g., "Zira"
    for voice in engine.getProperty('voices'):
        if "Zira" in voice.name:
            engine.setProperty('voice', voice.id)
            break

    sentences = text.split(". ")
    for sentence in sentences:
        if not sentence.strip():
            continue
        engine.say(sentence.strip())
        engine.runAndWait()
