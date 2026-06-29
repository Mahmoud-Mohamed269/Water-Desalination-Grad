"""
App settings loaded from .env file
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # ML Model paths (relative to backend/)
    WATER_QUALITY_MODEL_PATH: str = "ml/water_quality_rf.pkl"
    WATER_QUALITY_ENCODER_PATH: str = "ml/water_quality_encoder.pkl"
    MEMBRANE_MODEL_PATH: str = "ml/membrane_status_rf.pkl"
    MEMBRANE_ENCODER_PATH: str = "ml/membrane_encoder.pkl"


settings = Settings()
