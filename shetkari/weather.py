import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(lat, lon):

    if not API_KEY:
        return {
            "status": False,
            "message": "API Key not found."
        }

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}"
        f"&appid={API_KEY}"
        f"&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return {
                "status": False,
                "message": data.get("message", "Weather data not available.")
            }

        # Rainfall (Current weather मध्ये नसू शकतो)
        rainfall = 0

        if "rain" in data:
            rainfall = data["rain"].get("1h", data["rain"].get("3h", 0))

        return {
            "status": True,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "rainfall": rainfall,
            "description": data["weather"][0]["description"]
        }

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }