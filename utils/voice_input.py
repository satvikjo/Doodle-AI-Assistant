import speech_recognition as sr

def listen(timeout=5, retries=3):
    recognizer = sr.Recognizer()

    for attempt in range(retries):
        with sr.Microphone() as source:
            try:
                print("🎤 Listening for command...")
                audio = recognizer.listen(source, timeout=timeout)
                text = recognizer.recognize_google(audio)
                if text:
                    return text.strip().lower()
            except sr.WaitTimeoutError:
                print("⏳ No speech detected. Retrying...")
            except Exception as e:
                print(f"❌ Error during recognition: {e}")
                break

    return ""
