import pyttsx3
import threading
import time

_current_engine = None
_current_thread = None
_lock = threading.Lock()

def _create_engine():
    """Crée et configure un moteur pyttsx3"""
    engine = pyttsx3.init(driverName='espeak') 
    engine.setProperty('rate', 120)  
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "fr" in voice.id or "french" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    return engine

def read_story(story):
    """
    Lance la lecture du texte entier dans un thread.
    Si une lecture est déjà en cours, elle est stoppée proprement avant de lancer la nouvelle.
    """
    global _current_engine, _current_thread

    def _worker(engine, text):
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
        finally:
            time.sleep(0.05)
        return

    with _lock:
        if _current_engine is not None:
            try:
                _current_engine.stop()
            except Exception:
                pass
        if _current_thread is not None and _current_thread.is_alive():
            _current_thread.join(timeout=1.0)
        _current_engine = _create_engine()
        _current_thread = threading.Thread(target=_worker, args=(_current_engine, story), daemon=True)
        _current_thread.start()

def stop_reading():
    """Arrête la lecture en cours (appelé depuis l'UI)."""
    global _current_engine, _current_thread
    with _lock:
        if _current_engine is not None:
            try:
                _current_engine.stop()
            except Exception:
                pass
        if _current_thread is not None and _current_thread.is_alive():
            _current_thread.join(timeout=1.0)
