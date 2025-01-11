


import speech_recognition as sr
from time import ctime
import time
import os
from gtts import gTTS
import wolframalpha
from playsound import playsound


client = wolframalpha.Client("65QREL-J8L66PTWG8")

# Function to play text as speech
def speak(audioString):
    print(f"JARVIS: {audioString}")
    try:
        # Save audio to a temporary file
        tts = gTTS(text=audioString, lang='en')
        filename = "sample-0.mp3"
        tts.save(filename)
        
        # Play the audio file
        playsound(filename)
        
        # Remove the temporary audio file
        os.remove(filename)
    except Exception as e:
        print(f"Error in speak(): {e}")

# Function to record audio from the microphone
def recordAudio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("Processing...")
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            return "I couldn't understand that."
        except sr.RequestError as e:
            return f"Speech recognition error: {e}"
        except Exception as e:
            return f"Error while recording: {e}"

# Function to process user input and query WolframAlpha
def jarvis(data):
    try:
        res = client.query(data)
        result_text = next(res.results).text
        speak(result_text)
    except StopIteration:
        speak("I'm sorry, I couldn't find an answer.")
    except Exception as e:
        speak(f"An error occurred while querying WolframAlpha: {e}")

# Main script execution
time.sleep(2)
speak("Hi Noah, what can I do for you?")

while True:
    data = recordAudio()
    if "exit" in data.lower():
        speak("Goodbye, Noah!")
        break
    jarvis(data)
