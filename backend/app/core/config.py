"""
App settings loaded from .env file
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "serviceAccountKey.json"
    FIREBASE_SERVICE_ACCOUNT_BASE64: str = ""   # Set in Vercel env vars (base64-encoded JSON)
    FIREBASE_DATABASE_URL: str = "https://your-project-default-rtdb.firebaseio.com"

    # Gemini AI
    GEMINI_API_KEY: str = ""

    # FastAPI
    SECRET_KEY: str = "change_me_in_production"
    API_KEY: str = ""           # Set in .env — protects /ingest, /predict POST, /chat
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEFAULT_DEVICE_ID: str = "device_001"

    # ML Model paths (absolute paths for Vercel compatibility)
    WATER_QUALITY_MODEL_PATH: str = os.path.join(BASE_DIR, "ml", "water_quality_rf.pkl")
    WATER_QUALITY_ENCODER_PATH: str = os.path.join(BASE_DIR, "ml", "water_quality_encoder.pkl")
    MEMBRANE_MODEL_PATH: str = os.path.join(BASE_DIR, "ml", "membrane_status_rf.pkl")
    MEMBRANE_ENCODER_PATH: str = os.path.join(BASE_DIR, "ml", "membrane_encoder.pkl")


settings = Settings()
