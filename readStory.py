import pyttsx3
import time
import threading

def read_story(story):
    engine = pyttsx3.init(driverName='espeak') 
    engine.setProperty('rate', 120)
    engine.setProperty('volume', 1.0)

    voices = engine.getProperty('voices')
    for voice in voices:
        if "fr" in voice.id or "french" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    def speak():
        engine.say(story)
        engine.runAndWait()
        time.sleep(1)

    t = threading.Thread(target=speak)
    t.start()
    input("Appuyez sur Entrée pour arrêter la lecture...")
    engine.stop()
    t.join()
