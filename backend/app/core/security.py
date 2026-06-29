"""
API Key security dependency for FastAPI.
Sensitive write/ingest endpoints require: X-API-Key header.
Public read-only endpoints (live, history, status) remain open.
"""
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """
    FastAPI dependency — raises 403 if the X-API-Key header is missing or wrong.
    Usage:
        @router.post("/ingest", dependencies=[Depends(verify_api_key)])
    """
    if not settings.API_KEY:
        # API_KEY not configured — allow through (dev mode)
        return

    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key. Set X-API-Key header.",
        )
