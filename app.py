# import Requirementslibraries
import datetime
import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
import openai
from gtts import gTTS
import pygame
import os
import musicLibrary
import wikipedia
import secret_key  

recognizer = sr.Recognizer()
engine = pyttsx3.init()

# API Keys from secret_key module
NEWS_API_KEY = secret_key.news_api
OPENAI_API_KEY = secret_key.openai_api
WEATHER_API_KEY = secret_key.weather_api

# App shortcuts and website URLs
BUILD_IN_APP = {
    "open notepad": "C:\\Windows\\System32\\notepad.exe",
    "open chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "open word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "open excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
    "open powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
    "open python": "C:\\Users\\Kmoha\\AppData\\Local\\Programs\\Python\\Python310\\python.exe",
    "open code": "C:\\Users\\kmoha\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "open mongodb": "C:\\Users\\kmoha\\AppData\\Local\\MongoDBCompass\\MongoDBCompass.exe"
}

WEBSITES = {
    "open google": "https://google.com",
    "open youtube": "https://youtube.com",
    "open github": "https://github.com/ShaikhHamza104?tab=repositories",
    "open linkedin": "https://www.linkedin.com/feed/",
    "open stackoverflow": "https://stackoverflow.com/",
    "open gmail": "https://mail.google.com/mail/u/0/#inbox",
    "open discord": "https://discord.com/channels/@me",
    "open whatsapp": "https://web.whatsapp.com/",
    "open facebook": "https://www.facebook.com/",
    "open instagram": "https://www.instagram.com/",
    "open twitter": "https://twitter.com/home",
    "open spotify": "https://open.spotify.com/",
    "open tiktok": "https://www.tiktok.com/",
    "open netflix": "https://www.netflix.com/browse",
    "open amazon": "https://www.amazon.in/",
    "open flipkart": "https://www.flipkart.com/",
    "open chatgpt":"https://chatgpt.com/",
    "open w3schools":"https://www.w3schools.com/",
    "open udemy":"https://www.udemy.com/",
    "open udacity":"https://www.udacity.com/",
    "open coursera":"https://www.coursera.org/",
    "open edx":"https://www.edx.org/",
}

# Text-to-speech using gTTS and pygame
def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3')

    pygame.mixer.init()
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove('temp.mp3')

# Greeting based on the time of day
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am Jarvis sir. How may I help you?")

# Processing the command with OpenAI GPT
def aiProcess(command):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Jarvis skilled in general tasks like Alexa and Google Cloud. Give short responses, please."},
                {"role": "user", "content": command}
            ]
        )
        return completion.choices[0].message['content']
    except Exception as e:
        return f"Error with OpenAI API: {str(e)}"

# Get weather data for the specified city
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()
    if response["cod"] == 200:
        main = response['main']
        weather_description = response['weather'][0]['description']
        return f"Temperature: {main['temp']}°C, Description: {weather_description}"
    else:
        return "City not found."

# Command processor
def processCommand(c: str) -> str:
    c = c.lower()

    if c in BUILD_IN_APP:
        os.startfile(BUILD_IN_APP[c])

    elif c in WEBSITES:
        webbrowser.open(WEBSITES[c])

    elif c.startswith("play"):
        song = c.split(" ")[0]
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

    elif "time" in c:
        time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {time}")

    elif "date" in c:
        date = datetime.datetime.now().strftime("%d %B, %Y")
        speak(f"The date is {date}")

    elif "joke" in c:
        r = requests.get("https://official-joke-api.appspot.com/random_joke")
        if r.status_code == 200:
            joke = r.json()
            speak(f"{joke['setup']} ... {joke['punchline']}")
        else:
            speak("Sorry, I couldn't fetch a joke right now.")

    elif "wikipedia" in c:
        speak('Searching Wikipedia, sir.')
        query = c.replace("wikipedia", '')
        result = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia")
        speak(result)

    elif "weather" in c:
        speak("Say the city name.")
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

    elif "ai" in c:
        speak("What's your question?")
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            try:
                print("Listening for prompt...")
                audio = recognizer.listen(source)
                prompt = recognizer.recognize_google(audio)
                output = aiProcess(prompt)
                speak(output)
            except sr.UnknownValueError:
                speak("Sorry, I could not understand your prompt.")
            except sr.RequestError as e:
                speak(f"Could not request results from Google Speech Recognition; {e}")

    elif "stop" in c:
        speak("Bye!")
        exit()
    else:
        webbrowser.open(f"https://www.google.com/search?q={c}")

if __name__ == "__main__":
    wishMe()
    while True:
        try:
            with sr.Microphone() as source:
                recognizer = sr.Recognizer()
                print("Listening...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                word = recognizer.recognize_google(audio)
                if word.lower() == "jarvis":
                    speak("Yes?")
                    with sr.Microphone() as source:
                        audio = recognizer.listen(source)
                        command = recognizer.recognize_google(audio)
                        processCommand(command)
                else:
                    processCommand(word)
        except Exception as e:
            print(f"Error: {str(e)}")