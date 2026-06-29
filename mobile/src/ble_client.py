import asyncio
import json
import random
from database import save_sensor_reading

class VirtualBLEClient:
    """
    Simulates incoming ESP32 BLE broadcasts. 
    This allows us to test the Mobile App offline sync and UI on Windows.
    """
    def __init__(self):
        self.is_connected = False
        self._task = None

    async def connect(self):
        self.is_connected = True
        self._task = asyncio.create_task(self._simulate_broadcasts())
        return True

    async def disconnect(self):
        self.is_connected = False
        if self._task:
            self._task.cancel()
            
    async def _simulate_broadcasts(self):
        while self.is_connected:
            await asyncio.sleep(3) # Broadcast every 3 seconds
            
            # Simulated data matching our Phase 1 backend payload
            mock_data = {
                "ph": round(random.uniform(6.5, 7.5), 2),
                "tds": round(random.uniform(200, 300), 1),
                "turbidity": round(random.uniform(0.5, 2.5), 2),
                "water_temp_1": round(random.uniform(20, 25), 1),
                "pressure": round(random.uniform(2.0, 3.0), 2),
                "flow_rate": round(random.uniform(5.0, 10.0), 1),
                "ambient_temp": round(random.uniform(25, 30), 1),
                "ambient_humidity": round(random.uniform(40, 60), 1),
                "gas_1_ppm": round(random.uniform(10, 50), 1),
                "gas_2_ppm": round(random.uniform(5, 20), 1),
                "tank1_level_cm": round(random.uniform(10, 100), 1),
                "tank2_level_cm": round(random.uniform(10, 100), 1),
                "level_feed_full": True,
                "level_product_full": False,
                "pump_status": True,
                "valve_status": True
            }
            
            # Save directly to local SQLite db just like real BLE would
            save_sensor_reading(mock_data)

class RealBLEClient:
    """
    Connects to the physical ESP32 using the bleak library.
    (Requires Windows 10+ and a physical ESP32 broadcasting).
    """
    def __init__(self, service_uuid="12345678-1234-5678-1234-56789abcdef0"):
        self.service_uuid = service_uuid
        self.is_connected = False
        
    async def connect(self):
        try:
            from bleak import BleakScanner, BleakClient
            devices = await BleakScanner.discover(timeout=5.0)
            
            esp32 = None
            for d in devices:
                if d.name and "AquaMonitor" in d.name:
                    esp32 = d
                    break
                    
            if not esp32:
                print("ESP32 not found!")
                return False
                
            self.client = BleakClient(esp32)
            await self.client.connect()
            self.is_connected = True
            
            # Start notifications
            char_uuid = "87654321-4321-8765-4321-0fedcba98765"
            await self.client.start_notify(char_uuid, self._notification_handler)
            return True
        except ImportError:
            print("bleak not installed. Run: pip install bleak")
            return False
            
    async def disconnect(self):
        if self.is_connected and self.client:
            await self.client.disconnect()
        self.is_connected = False
        
    def _notification_handler(self, sender, data):
        try:
            payload = json.loads(data.decode('utf-8'))
            save_sensor_reading(payload)
        except Exception as e:
            print(f"Failed to parse BLE data: {e}")
