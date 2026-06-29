"""
Firebase Admin SDK initializer — supports both local file and
Vercel/cloud base64-encoded service account credentials.

Priority:
  1. FIREBASE_SERVICE_ACCOUNT_BASE64 env var  (Vercel / Railway)
  2. FIREBASE_SERVICE_ACCOUNT_PATH file        (local dev)
"""
import json
import base64
import firebase_admin
from firebase_admin import credentials, db
from app.core.config import settings

_firebase_app = None


def get_firebase_app():
    global _firebase_app
    if _firebase_app:
        return _firebase_app

    try:
        # ── Option 1: base64-encoded JSON in env var (cloud deploy) ──────
        if settings.FIREBASE_SERVICE_ACCOUNT_BASE64:
            decoded = base64.b64decode(
                settings.FIREBASE_SERVICE_ACCOUNT_BASE64
            ).decode("utf-8")
            service_account_info = json.loads(decoded)
            cred = credentials.Certificate(service_account_info)
            print("[Firebase] Initialized from FIREBASE_SERVICE_ACCOUNT_BASE64")

        # ── Option 2: path to JSON file (local dev) ───────────────────────
        else:
            cred = credentials.Certificate(
                settings.FIREBASE_SERVICE_ACCOUNT_PATH
            )
            print(f"[Firebase] Initialized from file: "
                  f"{settings.FIREBASE_SERVICE_ACCOUNT_PATH}")

        _firebase_app = firebase_admin.initialize_app(
            cred, {"databaseURL": settings.FIREBASE_DATABASE_URL}
        )
        print(f"[Firebase] DB URL: {settings.FIREBASE_DATABASE_URL}")

    except FileNotFoundError:
        print("[Firebase] WARNING: serviceAccountKey.json not found — "
              "running without Firebase sync.")
    except Exception as e:
        print(f"[Firebase] WARNING: Failed to initialize — {e}")

    return _firebase_app


# ── In-memory mock for when Firebase is unavailable ────────────────────
_mock_db: dict = {}


def get_db_ref(path: str):
    app = get_firebase_app()
    if not app:
        class MockRef:
            def __init__(self, p):
                self.p = p

            def push(self, data):
                if self.p not in _mock_db:
                    _mock_db[self.p] = []
                _mock_db[self.p].append(data)

            def get(self):
                val = _mock_db.get(self.p)
                if isinstance(val, list):
                    return {f"mock_id_{i}": v for i, v in enumerate(val)}
                return val

            def child(self, subpath):
                return MockRef(f"{self.p}/{subpath}")

            def set(self, data):
                _mock_db[self.p] = data

            def order_by_key(self):
                return self

            def limit_to_last(self, limit):
                outer = self

                class LimitMockRef(MockRef):
                    def get(self_inner):
                        val = _mock_db.get(outer.p, [])
                        if isinstance(val, list):
                            arr = val[-limit:]
                            return {f"mock_id_{i}": v
                                    for i, v in enumerate(arr)}
                        return outer.get()

                return LimitMockRef(outer.p)

        return MockRef(path)

    return db.reference(path)
