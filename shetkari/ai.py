import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def get_ai_advice(data):

    weather = data.get("weather", {})

    prompt = f"""
You are an expert agriculture assistant.

Analyze the following farm data.

Satellite Data:
- NDVI: {data.get('ndvi', 0)}
- NDWI: {data.get('ndwi', 0)}
- EVI: {data.get('evi', 0)}
- SAVI: {data.get('savi', 0)}

Weather Data:
- Temperature: {weather.get('temperature', 0)} °C
- Humidity: {weather.get('humidity', 0)} %
- Rainfall: {weather.get('rainfall', 0)} mm
- Wind Speed: {weather.get('wind_speed', 0)} km/h
- Weather: {weather.get('description', 'Unknown')}

Give the response in Marathi.

Include:
1. Crop Health
2. Disease Risk
3. Irrigation Advice
4. Fertilizer Advice
5. Pest Control

Keep the answer short using bullet points only.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text