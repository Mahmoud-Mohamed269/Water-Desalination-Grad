import subprocess
import time
import sys
import os
import threading
import webbrowser
import http.server
import socketserver

BACKEND_PORT = 8000
FRONTEND_PORT = 54321
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "dashboard", "web")

def serve_frontend():
    """Serve the HTML dashboard with a simple HTTP server."""
    os.chdir(FRONTEND_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *args: None  # silence logs
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", FRONTEND_PORT), handler) as httpd:
        print(f"  Dashboard: http://127.0.0.1:{FRONTEND_PORT}")
        httpd.serve_forever()

def start_services():
    print("\n[*] Water Desalination System Starting...\n")

    # Start FastAPI backend
    print("  [1/2] Starting FastAPI Backend on port", BACKEND_PORT)
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", str(BACKEND_PORT)],
        cwd=os.path.join(os.path.dirname(__file__), "backend")
    )

    # Wait for backend to boot
    time.sleep(3)

    # Start frontend in background thread
    print("  [2/2] Starting Web Dashboard on port", FRONTEND_PORT)
    t = threading.Thread(target=serve_frontend, daemon=True)
    t.start()

    time.sleep(1)
    print(f"\n[OK] All services running!")
    print(f"  FastAPI Docs: http://127.0.0.1:{BACKEND_PORT}/docs")
    print(f"  Dashboard:    http://127.0.0.1:{FRONTEND_PORT}")
    print("\nOpening browser...")
    webbrowser.open(f"http://127.0.0.1:{FRONTEND_PORT}")
    print("\nPress CTRL+C to stop all services.\n")

    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_process.terminate()
        backend_process.wait()
        print("Done.")

if __name__ == "__main__":
    start_services()
