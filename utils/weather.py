import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Buffalo"  # You can make this dynamic later

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code != 200:
        return "Sorry, I couldn't fetch the weather right now."

    data = response.json()
    temp = data['main']['temp']
    condition = data['weather'][0]['description']
    feels_like = data['main']['feels_like']
    
    return f"It's currently {temp}°C in {CITY} with {condition}. It feels like {feels_like}°C."

def will_it_rain():
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return "I couldn't check the rain forecast."

    forecast_data = response.json()['list'][:8]  # Next ~24 hours
    for entry in forecast_data:
        weather = entry['weather'][0]['main'].lower()
        if 'rain' in weather:
            return "Yes, it looks like it might rain within the next day."
    return "No rain expected in the next 24 hours."
