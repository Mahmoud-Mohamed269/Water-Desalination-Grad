"""
Vercel Python Serverless handler entry point.
Vercel expects a callable `app` in api/index.py (or main.py depending on vercel.json).
"""
from main import app  # re-export for Vercel
