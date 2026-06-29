import sqlite3
import os
import datetime
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'local_sensors.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create sensors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            synced INTEGER DEFAULT 0,
            data TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_sensor_reading(data_dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.utcnow().isoformat()
    
    cursor.execute(
        "INSERT INTO sensors (timestamp, data, synced) VALUES (?, ?, ?)",
        (timestamp, json.dumps(data_dict), 0)
    )
    conn.commit()
    conn.close()

def get_latest_reading():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM sensors ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def get_unsynced_readings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, data FROM sensors WHERE synced = 0")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "timestamp": r[1], "data": json.loads(r[2])} for r in rows]

def mark_as_synced(ids):
    if not ids: return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    placeholders = ','.join('?' * len(ids))
    cursor.execute(f"UPDATE sensors SET synced = 1 WHERE id IN ({placeholders})", ids)
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
