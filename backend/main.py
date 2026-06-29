"""
FastAPI Backend - Water Desalination Monitoring System
Main application entry point (Railway / Vercel-compatible)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import sensors, predict, alerts, chat, status

app = FastAPI(
    title="Water Desalination API",
    description="Backend API for the Water Desalination Monitoring System",
    version="1.0.0",
)

# CORS — restrict to known origins in production
# Add your Railway/Vercel URL here once deployed
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
    # Add deployed frontend URL e.g.:
    # "https://your-project.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(sensors.router, prefix="/api/v1/sensors",  tags=["Sensors"])
app.include_router(predict.router, prefix="/api/v1/predict",  tags=["ML Predictions"])
app.include_router(alerts.router,  prefix="/api/v1/alerts",   tags=["Alerts"])
app.include_router(chat.router,    prefix="/api/v1/chat",     tags=["Gemini AI Chat"])
app.include_router(status.router,  prefix="/api/v1/status",   tags=["System Status"])


@app.get("/")
def root():
    return {
        "message": "Water Desalination API is running.",
        "docs": "/docs",
    }
