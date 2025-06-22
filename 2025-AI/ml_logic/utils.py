# ml_logic/utils.py
import requests
import os
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env file in the root directory

def get_weather(city: str):
    """
    Fetches current weather for a given city.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Warning: OpenWeatherMap API key not found in .env file.")
        return None
        
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric' # Use Celsius
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (like 401, 404)
        data = response.json()
        
        weather = {
            'temp': data['main']['temp'],
            'description': data['weather'][0]['main'].lower(), # e.g., 'clear', 'clouds', 'rain'
            'city': data['name']
        }
        return weather
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        return None