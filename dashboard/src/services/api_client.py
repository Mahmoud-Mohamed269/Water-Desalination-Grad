# dashboard/src/services/api_client.py
import requests
from utils.constants import API_BASE_URL

def get_live_sensors():
    try:
        response = requests.get(f"{API_BASE_URL}/sensors/live", timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching live sensors: {e}")
    return None

def get_predictions():
    try:
        response = requests.post(f"{API_BASE_URL}/predict", timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching predictions: {e}")
    return None

def send_chat_message(message, context=None):
    try:
        payload = {"message": message, "context": context or {}}
        response = requests.post(f"{API_BASE_URL}/chat/", json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error sending chat message: {e}")
    return None
