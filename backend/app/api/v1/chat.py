"""
/api/v1/chat — Gemini AI proxy for the dashboard/mobile chatbot
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
from app.core.config import settings

router = APIRouter()

# Initialize the new Google GenAI client
try:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
except Exception:
    client = None

SYSTEM_PROMPT = """You are an expert AI assistant specializing in water desalination systems, 
RO membranes, water quality analysis, and industrial IoT sensor interpretation.
Answer questions clearly and concisely. When given sensor values, interpret them in the context 
of a Reverse Osmosis desalination system and WHO drinking water quality standards.
If a sensor reading suggests a problem, clearly explain the likely cause and recommended action."""


@router.post("/")
def chat(request: dict):
    """
    Sends a user message to Gemini and returns the response.
    Accepts: {"message": "...", "context": {...}}
    """
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client not configured. Check API key.")

    try:
        user_message = request.get("message", "")
        context = request.get("context", {})

        if not user_message:
            raise HTTPException(status_code=400, detail="message is required")

        # Build prompt with sensor context if provided
        full_prompt = SYSTEM_PROMPT
        if context:
            full_prompt += f"\n\nCurrent sensor readings: {context}"
        full_prompt += f"\n\nUser: {user_message}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )

        return {
            "status": "ok",
            "reply": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
