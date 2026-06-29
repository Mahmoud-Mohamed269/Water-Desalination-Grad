"""
/api/v1/status — System health and device status
"""
from fastapi import APIRouter, HTTPException
from app.core.firebase import get_db_ref

router = APIRouter()
DEVICE_ID = "device_001"


@router.get("/")
def get_system_status_default():
    """Returns the last known system status from Firebase for default device."""
    return _get_status(DEVICE_ID)


@router.get("/{device_id}")
def get_system_status(device_id: str):
    """Returns the last known system status from Firebase for the given device."""
    return _get_status(device_id)


def _get_status(device_id: str):
    try:
        data = get_db_ref(f"/system_status/{device_id}").get()
        if data is None:
            # No status entry yet — return a healthy default so dashboard shows ONLINE
            return {"status": "ok", "system": {"online": True, "device_id": device_id}}
        return {"status": "ok", "system": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health_check():
    """Simple liveness probe for Vercel / uptime monitors."""
    return {"status": "healthy", "service": "water-desalination-api"}
