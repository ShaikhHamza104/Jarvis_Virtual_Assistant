import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
import openai  # Corrected import for OpenAI
from gtts import gTTS
import pygame
import os
import musicLibrary
import secret_key 
recognizer = sr.Recognizer()
engine = pyttsx3.init() 
NEWS_API_KEY = secret_key.news_api
OPENAI_API_KEY = secret_key.openai
WHEATHER_API_KEY = secret_key.weather_api_key
BUILD_IN_APP={
        "open notepad": "C:\\Windows\\System32\\notepad.exe",
        "open chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "open word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        "open excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
        "open powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE"
}
def speak_old(text):
    engine.say(text)
    engine.runAndWait()

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3') 

    pygame.mixer.init()

    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3")

def aiProcess(command):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Jarvis skilled in general tasks like Alexa and Google Cloud. Give short responses, please."},
                {"role": "user", "content": command}
            ]
        )
        return completion.choices[0].message['content']
    except Exception as e:
        return f"Error with OpenAI API: {str(e)}"
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WHEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()
    if response["cod"] == 200:
        main = response['main']
        weather_description = response['weather'][0]['description']
        return f"Temperature: {main['temp']}°C, Description: {weather_description}"
    else:
        return "City not found."

def processCommand(c):
    c = c.lower()  # Ensure case-insensitivity
    if c in BUILD_IN_APP:
        os.startfile(BUILD_IN_APP[c])
    elif c == "open facebook":
        webbrowser.open("https://www.facebook.com/")
    elif c == "open whatsapp":
        webbrowser.open("https://web.whatsapp.com/")
    elif c == "open github":
        webbrowser.open("https://github.com/ShaikhHamza104?tab=repositories")
    elif c == "open linkedin":
        webbrowser.open("https://www.linkedin.com/feed/")
    elif c == "open youtube":
        webbrowser.open("https://youtube.com")
    elif c.startswith("play"):
        song = c.split(" ")[1]
        link = musicLibrary.music.get(song, None)
        if link:
            webbrowser.open(link)
        else:
            speak(f"Sorry, I could not find the song {song}")
    elif "news" in c:
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            for article in articles:
                speak(article['title'])
        else:
            speak("Failed to fetch news")
    elif "weather" in c:
        if "weather" in c:
            speak("Say the city name.")
            
            # Use the microphone to capture the city name
            with sr.Microphone() as source:
                recognizer = sr.Recognizer()
                try:
                    print("Listening for city name...")
                    audio = recognizer.listen(source)
                    city = recognizer.recognize_google(audio)
                    print(f"City recognized: {city}")
                    
                    weather = get_weather(city)
                    speak(weather)
                except sr.UnknownValueError:
                    speak("Sorry, I could not understand the city name.")
                except sr.RequestError as e:
                    speak(f"Could not request results from Google Speech Recognition; {e}")
    else:
        output = aiProcess(c)
        speak(output)

if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        recognizer = sr.Recognizer()
        print("recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            word = recognizer.recognize_google(audio)
            if word.lower() == "google":
                speak("Ya")
                with sr.Microphone() as source:
                    print("Jarvis Active...")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)
                print("Jarvis Inactive...")
                speak("Jarvis Inactive")
                break
            else:
                processCommand(word)
        except Exception as e:
            print(f"Error: {str(e)}")