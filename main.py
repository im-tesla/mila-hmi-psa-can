#!/usr/bin/env python3
"""CAN Diagnostic Terminal — single command launcher."""

import os
import sys
import subprocess


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    bridge = os.path.join(root, "can-bridge")

    # Frontend must be built first
    dist = os.path.join(root, "frontend", "dist")
    if not os.path.exists(os.path.join(dist, "index.html")):
        print("[BUILD] Frontend not built — running npm build...")
        frontend = os.path.join(root, "frontend")
        subprocess.run(["npm", "install"], cwd=frontend, check=True)
        subprocess.run(["npm", "run", "build"], cwd=frontend, check=True)

    # Install Python deps if needed
    try:
        import fastapi, uvicorn, serial  # noqa: F401
    except ImportError:
        print("[DEPS] Installing Python dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r",
             os.path.join(bridge, "requirements.txt")],
            check=True,
        )

    # Run the bridge
    print("[START] Launching CAN Diagnostic Terminal...")
    os.chdir(bridge)
    sys.path.insert(0, bridge)
    import runpy
    runpy.run_path("main.py", run_name="__main__")


if __name__ == "__main__":
    main()
