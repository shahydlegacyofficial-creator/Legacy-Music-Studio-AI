from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COMFY = ROOT / "ComfyUI"
LOG = ROOT / "comfyui-engine.log"
ENGINE_URL = "http://127.0.0.1:8188/system_stats"
DASHBOARD_URL = "http://127.0.0.1:8787"


def engine_ready() -> bool:
    try:
        with urllib.request.urlopen(ENGINE_URL, timeout=2) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def log_tail(lines: int = 35) -> str:
    try:
        return "\n".join(LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:])
    except OSError:
        return "The engine log was not created."


def start_engine() -> tuple[subprocess.Popen | None, object | None]:
    if engine_ready():
        print("MiniMax engine is already running.")
        return None, None

    LOG.write_text("", encoding="utf-8")
    log_handle = LOG.open("a", encoding="utf-8")
    command = [
        sys.executable,
        str(COMFY / "main.py"),
        "--listen", "127.0.0.1",
        "--port", "8188",
        "--lowvram",
        "--preview-method", "none",
        "--disable-auto-launch",
    ]
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        creationflags=flags,
        env={**os.environ, "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"},
    )
    return process, log_handle


def wait_for_engine(process: subprocess.Popen | None, timeout: int = 300) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if engine_ready():
            print("\nMiniMax engine ready.")
            return
        if process is not None and process.poll() is not None:
            raise RuntimeError(
                f"The MiniMax engine stopped during startup (exit code {process.returncode}).\n\n"
                f"Last engine messages:\n{log_tail()}"
            )
        print(".", end="", flush=True)
        time.sleep(2)
    raise RuntimeError(f"The MiniMax engine did not become ready within five minutes.\n\nLast engine messages:\n{log_tail()}")


def main() -> int:
    if not (COMFY / "main.py").is_file():
        print("The low-VRAM engine is missing. Run setup_low_vram_windows.bat first.")
        return 1

    print("Starting the hidden MiniMax Music 3 INT8 engine...")
    process = None
    log_handle = None
    try:
        process, log_handle = start_engine()
        print("Waiting for the engine", end="", flush=True)
        wait_for_engine(process)
        print(f"Opening Legacy Music Studio at {DASHBOARD_URL}")
        threading.Timer(2, lambda: webbrowser.open(DASHBOARD_URL)).start()

        import uvicorn

        uvicorn.run("app:app", host="127.0.0.1", port=8787, log_level="warning")
        return 0
    except Exception as exc:
        print(f"\n\nSTARTUP ERROR\n{exc}")
        print(f"\nFull engine log: {LOG}")
        return 1
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
        if log_handle is not None:
            log_handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
