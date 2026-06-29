import asyncio
import json
from bleak import BleakClient, BleakScanner
from db.local_db import save_reading

# UUIDs must match Main_Hub/config.h
BLE_SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
BLE_NOTIFY_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
BLE_WRITE_CHAR_UUID = "cba1d466-344c-4be3-ab3f-189f80dd7518"

class RealBLEClient:
    def __init__(self, device_name="AquaMonitor"):
        self.device_name = device_name
        self.client = None
        self.connected = False

    async def connect(self):
        print(f"[BLE] Scanning for {self.device_name}...")
        while not self.connected:
            try:
                devices = await BleakScanner.discover(timeout=5.0)
                target_device = None
                for d in devices:
                    if d.name and self.device_name in d.name:
                        target_device = d
                        break

                if target_device:
                    print(f"[BLE] Found {self.device_name}. Connecting...")
                    self.client = BleakClient(target_device)
                    await self.client.connect()
                    self.connected = True
                    print("[BLE] Connected!")
                    
                    # Start listening to notifications
                    await self.client.start_notify(BLE_NOTIFY_CHAR_UUID, self._notification_handler)
                    
                    # Keep connection alive
                    while self.client.is_connected:
                        await asyncio.sleep(1)
                    
                    print("[BLE] Disconnected.")
                    self.connected = False
            except Exception as e:
                print(f"[BLE] Connection error: {e}")
            
            await asyncio.sleep(3) # Retry delay

    def _notification_handler(self, sender, data):
        try:
            payload = data.decode('utf-8')
            reading = json.loads(payload)
            save_reading(reading)
        except Exception as e:
            print(f"[BLE] Failed to parse notification: {e}")
            
    async def send_command(self, cmd_dict):
        if not self.connected or not self.client:
            print("[BLE] Cannot send command, not connected.")
            return False
        try:
            payload = json.dumps(cmd_dict).encode('utf-8')
            await self.client.write_gatt_char(BLE_WRITE_CHAR_UUID, payload, response=True)
            print(f"[BLE] Sent command: {cmd_dict}")
            return True
        except Exception as e:
            print(f"[BLE] Failed to send command: {e}")
            return False

class VirtualBLEClient:
    """Mock BLE client for UI testing when hardware is unavailable"""
    def __init__(self):
        self.connected = False
        
    async def connect(self):
        print("[VirtualBLE] Simulating connection...")
        await asyncio.sleep(2)
        self.connected = True
        print("[VirtualBLE] Connected!")
        
        import random
        # Simulate receiving data every 3 seconds
        while True:
            mock_data = {
                "ph_feed": round(random.uniform(6.5, 8.5), 2),
                "ph_permeate": round(random.uniform(6.8, 7.5), 2),
                "tds_feed": round(random.uniform(200, 500), 1),
                "tds_permeate": round(random.uniform(10, 50), 1),
                "pressure_feed": round(random.uniform(2.0, 5.0), 2),
                "turbidity_feed": round(random.uniform(0.5, 3.0), 2),
                "temperature_feed": round(random.uniform(20.0, 30.0), 1),
                "flow_rate_feed": round(random.uniform(10.0, 15.0), 1),
                "water_level_feed_tank": 100 if random.random() > 0.1 else 0,
                "pump_status": "running" if random.random() > 0.2 else "stopped",
                "recovery_rate": round(random.uniform(40, 60), 1),
                "rejection_rate": round(random.uniform(90, 99), 1)
            }
            save_reading(mock_data)
            await asyncio.sleep(3)
            
    async def send_command(self, cmd_dict):
        print(f"[VirtualBLE] Simulated sending command: {cmd_dict}")
        return True
