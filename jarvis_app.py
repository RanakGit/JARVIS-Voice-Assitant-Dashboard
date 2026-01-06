import webbrowser
import sounddevice as sd
import numpy as np
import time
import vosk
import json
import os
import requests
from gtts import gTTS
import pyglet


import musiclibrary

# ---------------- CONFIG ----------------
newsapi = "a2a9cc7383ea434c8d23537972a32b9"  # Replace with your NewsAPI key

MODEL_PATH = r"C:\Users\User\Downloads\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"



# ---------------- AUDIO DEVICES ----------------
print("Available audio devices:")
print(sd.query_devices())

# ---------------- LOAD VOSK MODEL ----------------
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Vosk model not found")

model = vosk.Model(MODEL_PATH)

# ---------------- TTS (gTTS + pyglet) ----------------
def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        tts.save("temp.mp3")

        music = pyglet.media.load("temp.mp3")
        player = pyglet.media.Player()
        player.queue(music)
        player.play()

        pyglet.clock.schedule_once(
            lambda dt: pyglet.app.exit(), music.duration
        )
        pyglet.app.run()

        os.remove("temp.mp3")

    except Exception as e:
        print("Speech Error:", e)

# ---------------- NOISE CALIBRATION ----------------
def calibrate_noise(duration=1.0, fs=16000):
    speak("Calibrating noise. Please stay silent.")
    time.sleep(1)

    sd.default.device = 0
    sd.default.samplerate = fs
    sd.default.channels = 1

    noise = sd.rec(int(duration * fs), dtype="int16")
    sd.wait()

    rms = np.sqrt(np.mean(noise.astype(np.float32) ** 2))
    return max(300, int(rms * 1.2))

# ---------------- SPEECH RECOGNITION ----------------
def record_and_recognize(duration=5, fs=16000):
    sd.default.device = 0
    sd.default.samplerate = fs
    sd.default.channels = 1

    audio = sd.rec(int(duration * fs), dtype="int16")
    sd.wait()

    rec = vosk.KaldiRecognizer(model, fs)
    rec.AcceptWaveform(audio.tobytes())
    result = json.loads(rec.FinalResult())

    return result.get("text", "").lower()



# ---------------- MAIN LOOP ----------------
if __name__ == "__main__":
    speak("Initializing jarvis. Welcome back sir.")
    time.sleep(0.5)

    calibrate_noise()
    print("Listening for wake word jarvis")

    while True:
        try:
            command = record_and_recognize(5)

            if command:
                print("Heard:", command)

            if "jarvis" in command:
                speak("Yes. How can I help you?")
                time.sleep(0.5)

                command = record_and_recognize(8)
                print("Command:", command)

                if "google" in command:
                    speak("Opening Google")
                    webbrowser.open("https://www.google.com")

                elif "facebook"  in command:
                    speak("Opening Facebook")
                    webbrowser.open("https://www.facebook.com")

                elif "linkedin" in command or "linked in" in command:
                    speak("Opening LinkedIn")
                    webbrowser.open("https://www.linkedin.com")

                elif "youtube" in command or "you tube" in command:
                    speak("Opening YouTube")
                    webbrowser.open("https://www.youtube.com")

                elif "play" in command:
                    song = command.split()[-1]
                    if song in musiclibrary.music:
                        webbrowser.open(musiclibrary.music[song])
                        speak(f"Playing {song}")
                    else:
                        speak("Song not found")

                elif "news" in command:
                    r = requests.get(
                        f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}"
                    )
                    if r.status_code == 200:
                        for article in r.json().get("articles", [])[:5]:
                            speak(article["title"])

                elif "stop" in command or "exit" in command or "quit" in command:
                    speak("Goodbye sir.")
                    break

                

            time.sleep(0.1)

        except KeyboardInterrupt:
            speak("Shutting down. Goodbye.")
            break

        except Exception as e:
            print("Error:", e)
            time.sleep(0.2)
