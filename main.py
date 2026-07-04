from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from gee import analyze_crop
from weather import get_weather
from ai import get_ai_advice

# 1. नवीन Imports जोडले 
import os
from google import genai
from dotenv import load_dotenv

# 2. पर्यावरण व्हेरिएबल्स लोड केले आणि Gemini Client सेट केला
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

app = FastAPI(title="Smart Crop Health API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Farm(BaseModel):
    polygon: List[List[float]]


# 3. Farm class च्या खाली नवीन ChatRequest क्लास जोडला
class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "status": True,
        "message": "Smart Crop Health API Running 🚜"
    }


@app.post("/analyze-crop")
def analyze(data: Farm):

    # -------------------------
    # Satellite Analysis
    # -------------------------
    result = analyze_crop(data.polygon)

    if not result["status"]:
        return result

    # -------------------------
    # Weather
    # -------------------------
    lat = data.polygon[0][1]
    lon = data.polygon[0][0]

    weather = get_weather(lat, lon)

    result["weather"] = weather

    # -------------------------
    # Gemini AI Recommendation
    # -------------------------
    try:
        result["ai_advice"] = get_ai_advice(result)
    except Exception as e:
        result["ai_advice"] = f"AI Error: {str(e)}"

    return result


# 4. फाईलच्या शेवटी नवीन /chat-assistant एंडपॉईंट जोडला
@app.post("/chat-assistant")
def chat_ai(chat: ChatRequest):

    prompt = f"""
तू महाराष्ट्रातील शेतकऱ्यांसाठी AI कृषी तज्ञ आहेस.

उत्तर नेहमी मराठीत दे.

शेतकऱ्याचा प्रश्न:
{chat.question}

उत्तर सोप्या भाषेत दे.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "reply": response.text
    }