"""
Build all scenes to SVG, then serve the app.
Usage: python run.py
Then open http://localhost:8000/frontend/
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    print("Building scenes...")
    r = subprocess.run(
        [sys.executable, str(ROOT / "renderer" / "render.py")],
        cwd=str(ROOT),
    )
    if r.returncode != 0:
        sys.exit(r.returncode)
    print("Starting server at http://localhost:8000")
    print("Open http://localhost:8000/frontend/")
    subprocess.run(
        [sys.executable, "-m", "http.server", "8000"],
        cwd=str(ROOT),
    )

if __name__ == "__main__":
    main()
