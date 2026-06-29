import asyncio
import requests
from database import get_unsynced_readings, mark_as_synced

API_URL = "http://127.0.0.1:8000/api/v1/sensors/ingest"

async def sync_data_loop():
    """
    Background worker that constantly checks the SQLite database for 
    unsynced readings and pushes them to the backend when online.
    """
    while True:
        try:
            unsynced = get_unsynced_readings()
            if not unsynced:
                await asyncio.sleep(5)
                continue
                
            # Attempt to push to server
            synced_ids = []
            for record in unsynced:
                try:
                    response = requests.post(API_URL, json=record["data"], timeout=3)
                    if response.status_code == 200:
                        synced_ids.append(record["id"])
                    else:
                        print(f"Sync failed for id {record['id']}: {response.status_code} {response.text}")
                except requests.RequestException:
                    break # Server is offline, stop trying this batch
            
            # Mark successfully pushed records in local DB
            if synced_ids:
                mark_as_synced(synced_ids)
                
        except Exception as e:
            print(f"Sync error: {e}")
            
        await asyncio.sleep(5)
