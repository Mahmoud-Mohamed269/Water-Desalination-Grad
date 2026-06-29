import asyncio
import aiohttp
import json
from .local_db import get_unsynced, mark_synced, get_setting

async def sync_data_loop():
    """Background task to sync local SQLite data to FastAPI backend"""
    while True:
        try:
            # 1. Check if backend URL is configured
            api_url = get_setting("api_url", "http://127.0.0.1:8000")
            if not api_url.endswith("/"): api_url += "/"
            
            # 2. Get unsynced records
            records = get_unsynced(limit=10)
            if records:
                synced_ids = []
                async with aiohttp.ClientSession() as session:
                    for r_id, r_data in records:
                        try:
                            payload = json.loads(r_data)
                            async with session.post(f"{api_url}api/v1/sensors/ingest", json=payload, timeout=2) as resp:
                                if resp.status == 200:
                                    synced_ids.append(r_id)
                        except:
                            pass # Skip failing records, try again later
                
                # 3. Mark as synced locally
                if synced_ids:
                    mark_synced(synced_ids)
                    print(f"[Sync Worker] Synced {len(synced_ids)} records to backend.")
            
        except Exception as e:
            print(f"[Sync Worker] Error: {e}")
            
        # Wait before next sync cycle
        await asyncio.sleep(5)
