#!/usr/bin/env python3
"""
Cross-Platform Development Launcher for CardioPulse.

Launches the FastAPI backend server (Uvicorn on port 8001) and Vite frontend server
(on port 3000) concurrently across Windows, Linux, and containerized environments (Google AI Studio).
Handles graceful shutdown on SIGINT/Ctrl+C.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_nginx_check():
    """Attempt to run ensure_nginx_gateway.py safely without failing on non-Linux OS."""
    ensure_script = PROJECT_ROOT / "scripts" / "ensure_nginx_gateway.py"
    if ensure_script.exists():
        try:
            subprocess.run([sys.executable, str(ensure_script)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def main():
    os.chdir(PROJECT_ROOT)
    
    # 1. Run gateway setup check
    run_nginx_check()

    processes = []
    try:
        # 2. Start Uvicorn backend server on port 8001
        print("Starting CardioPulse FastAPI backend server on http://127.0.0.1:8001...")
        backend_cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
        ]
        backend_proc = subprocess.Popen(backend_cmd, cwd=PROJECT_ROOT)
        processes.append(backend_proc)

        # Give backend a moment to bind to port
        time.sleep(1.5)

        # 3. Start Vite frontend dev server on port 3000
        print("Starting CardioPulse Vite frontend server on http://0.0.0.0:3000...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        vite_cmd = [npm_cmd, "exec", "vite", "--", "--port=3000", "--host=0.0.0.0"]
        
        vite_proc = subprocess.Popen(vite_cmd, cwd=PROJECT_ROOT)
        processes.append(vite_proc)

        # Wait for processes
        for proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        print("\nShutting down CardioPulse development servers...")
        for proc in processes:
            try:
                proc.terminate()
            except Exception:
                pass
        sys.exit(0)

if __name__ == "__main__":
    main()
