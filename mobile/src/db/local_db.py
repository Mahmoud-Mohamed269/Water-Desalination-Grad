import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sensor_data.sqlite")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            data TEXT,
            synced INTEGER DEFAULT 0
        )
    ''')
    
    # Store settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_reading(data_dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        ts = datetime.utcnow().isoformat() + "Z"
        if "timestamp" in data_dict:
            ts = data_dict["timestamp"]
        else:
            data_dict["timestamp"] = ts
            
        cursor.execute("INSERT INTO readings (timestamp, data, synced) VALUES (?, ?, 0)",
                       (ts, json.dumps(data_dict)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Save error: {e}")

def get_latest_reading():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM readings ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
    except:
        pass
    return None

def get_history(limit=50):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM readings ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        # Return in chronological order
        return [json.loads(row[0]) for row in reversed(rows)]
    except:
        pass
    return []

def get_unsynced(limit=50):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, data FROM readings WHERE synced=0 LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except:
        return []

def mark_synced(ids):
    if not ids: return
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(ids))
        cursor.execute(f"UPDATE readings SET synced=1 WHERE id IN ({placeholders})", ids)
        conn.commit()
        conn.close()
    except:
        pass

def get_setting(key, default=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    except:
        return default

def save_setting(key, value):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()
    except:
        pass

init_db()
