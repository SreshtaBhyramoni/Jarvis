from __future__ import annotations

import datetime as _dt
import sys
import webbrowser

# Third‑party packages
import pyttsx3
import pywhatkit
import wikipedia
import pyjokes

# SpeechRecognition and mic input (optional if you use keyboard fallback)
import speech_recognition as sr


# Configuration

WAKE_WORDS = ("jarvis", "hey jarvis")  # You can say "Jarvis ..." before a command (optional)
USE_TEXT_INPUT = False  # Set True to type commands instead of using microphone
VOICE_RATE = 180        # TTS speed (words per minute). Try 160–190 for clarity


# Speech: Text → Speech

engine = pyttsx3.init()
engine.setProperty("rate", VOICE_RATE)
# Optional: choose a voice (0/1 on many systems). Comment out if not needed.
voices = engine.getProperty("voices")
if voices:
    try:
        # engine.setProperty("voice", voices[1].id)  # often a female voice; adjust index if you prefer
        engine.setProperty("voice", voices[0].id)
    except Exception:
        pass


def speak(text: str) -> None:
    """Speak text aloud and also print it for visibility."""
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()


# Listening: Speech → Text

_recognizer = sr.Recognizer()


def listen(timeout: int = 5, phrase_time_limit: int = 8) -> str:
    """Listen from the default microphone and return lower‑cased text.
    Returns empty string on failure.
    """
    try:
        with sr.Microphone() as source:
            _recognizer.adjust_for_ambient_noise(source, duration=0.6)
            print("Listening… (speak now)")
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        text = _recognizer.recognize_google(audio)
        return text.lower().strip()
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        speak("Sorry, I couldn't catch that. Please repeat.")
        return ""
    except sr.RequestError:
        speak("Speech service seems unavailable. You can type commands for now.")
        return ""
    except Exception as e:
        print(f"[listen] error: {e}")
        return ""


# Helpers


def greet() -> None:
    hour = _dt.datetime.now().hour
    if 5 <= hour < 12:
        speak("Good morning, Sreshta.")
    elif 12 <= hour < 18:
        speak("Good afternoon, Sreshta.")
    else:
        speak("Good evening, Sreshta.")
    speak("Jarvis online. Say a command, or say 'exit' to quit.")


def _maybe_strip_wakeword(text: str) -> str:
    for w in WAKE_WORDS:
        if text.startswith(w):
            return text.replace(w, "", 1).strip()
    return text



# Command router


def process_command(cmd: str) -> bool:
    """Return False to exit, True to continue."""
    import urllib.parse as _uq

    if not cmd:
        return True

    cmd = _maybe_strip_wakeword(cmd)

    # 1) Exit
    if any(word in cmd for word in ("exit", "quit", "sleep", "stop")):
        speak("Powering down. Bye, Sreshta!")
        return False

    # 2) Time
    if "time" in cmd:
        now = _dt.datetime.now().strftime("%I:%M %p")
        speak(f"It's {now}.")
        return True

    # 3) Open websites
    if "open youtube" in cmd:
        speak("Opening YouTube.")
        webbrowser.open("https://www.youtube.com")
        return True

    if "open google" in cmd:
        speak("Opening Google.")
        webbrowser.open("https://www.google.com")
        return True

     # Play on YouTube (e.g., "play kesariya on youtube")
    if cmd.startswith("play "):
        query = cmd.replace("play ", "", 1).replace("on youtube", "").strip()
        if query:
            speak(f"Playing {query} on YouTube.")
            try:
                pywhatkit.playonyt(query)
            except Exception:
                speak("Couldn't open YouTube for that. Try again.")
        else:
            speak("What should I play?")
        return True

    #  Wikipedia quick answer (e.g., "wikipedia virat kohli" or "who is virat kohli")
    if "wikipedia" in cmd or cmd.startswith("who is ") or cmd.startswith("what is "):
        query = cmd.replace("wikipedia", "").replace("who is", "").replace("what is", "").strip()
        if query:
            speak(f"Searching Wikipedia for {query}.")
            try:
                summary = wikipedia.summary(query, sentences=2)
                speak(summary)
            except wikipedia.exceptions.DisambiguationError as e:
                speak("That term has multiple meanings. Please be more specific.")
                print(f"Disambiguation options: {e.options[:10]}")
            except wikipedia.exceptions.PageError:
                speak("Couldn't find a Wikipedia page for that.")
            except Exception:
                speak("Wikipedia seems busy. Try again in a bit.")
        else:
            speak("Tell me what to search on Wikipedia.")
        return True

    # Joke
    if "joke" in cmd:
        try:
            joke = pyjokes.get_joke()
            speak(joke)
        except Exception:
            speak("I tried to find a joke, but something went wrong.")
        return True

    # Fallback: offer a Google search
    speak("Want me to search that on the web?")
    webbrowser.open("https://www.google.com/search?q=" + _uq.quote(cmd))
    return True



# Main loop


def main() -> None:
    greet()
    while True:
        try:
            if USE_TEXT_INPUT:
                cmd = input("You: ").lower().strip()
            else:
                cmd = listen()
                if cmd:
                    print(f"You said: {cmd}")
            if not process_command(cmd):
                break
        except KeyboardInterrupt:
            speak("Interrupted. See you soon!")
            break
        except Exception as e:
            print(f"[main] error: {e}")
            speak("Something went wrong. Let's keep going.")


if __name__ == "__main__":
    main()

