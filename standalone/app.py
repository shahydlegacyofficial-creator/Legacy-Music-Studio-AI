from __future__ import annotations

import asyncio
import json
import os
import subprocess
import threading
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from comfy_runtime import ComfyUIRuntime

ROOT = Path(__file__).resolve().parent
OUTPUTS = Path(os.getenv("LEGACY_MUSIC_OUTPUTS", ROOT / "outputs"))
OUTPUTS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Legacy Music Studio", version="3.0.0")
runtime = ComfyUIRuntime()
generation_lock = threading.Lock()


@lru_cache(maxsize=1)
def hardware_profile():
    """Return a conservative duration tier from the installed NVIDIA VRAM."""
    profile = {
        "gpu_name": "NVIDIA GPU",
        "vram_total_mb": 0,
        "vram_free_mb": 0,
        "max_duration_seconds": 30,
        "tier": "LOW VRAM SAFE",
        "detected": False,
    }
    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if completed.returncode != 0 or not completed.stdout.strip():
            return profile
        name, total, free = [part.strip() for part in completed.stdout.splitlines()[0].split(",", 2)]
        total_mb = int(float(total))
        free_mb = int(float(free))
        max_duration = 120 if total_mb >= 22_000 else 60 if total_mb >= 14_000 else 30
        tier = "2 MINUTE ELIGIBLE" if max_duration == 120 else "1 MINUTE ELIGIBLE" if max_duration == 60 else "LOW VRAM SAFE"
        return {
            "gpu_name": name,
            "vram_total_mb": total_mb,
            "vram_free_mb": free_mb,
            "max_duration_seconds": max_duration,
            "tier": tier,
            "detected": True,
        }
    except (OSError, ValueError, subprocess.SubprocessError):
        return profile


class GenerationRequest(BaseModel):
    model: str = "MiniMaxAI/MiniMax-Music3"
    input: str = Field(min_length=1, max_length=50000)
    instructions: str = Field(min_length=1, max_length=50000)
    response_format: str = "flac"
    seed: int = Field(default=7, ge=0, le=2_147_483_647)
    max_new_tokens: int = Field(default=1500, ge=25, le=9000)
    stream: bool = False


@app.get("/api/status")
def status():
    return runtime.status()


@app.post("/api/setup")
def setup_model():
    runtime.start_loading()
    return runtime.status()


@app.get("/api/hardware")
def hardware():
    return hardware_profile()


@app.get("/api/library")
def library():
    tracks = []
    for audio_path in sorted(OUTPUTS.glob("*.flac"), key=lambda item: item.stat().st_mtime, reverse=True):
        metadata_path = audio_path.with_suffix(".json")
        metadata = {}
        if metadata_path.is_file():
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                metadata = {}
        stat = audio_path.stat()
        tracks.append({
            "filename": audio_path.name,
            "url": f"/outputs/{quote(audio_path.name)}",
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            **metadata,
        })
    return {"tracks": tracks}


@app.get("/v1/models")
def models():
    return {"data": [{"id": "MiniMaxAI/MiniMax-Music3", "object": "model"}]}


@app.post("/v1/audio/speech")
async def generate_music(request: GenerationRequest):
    if request.response_format.lower() not in {"wav", "mp3", "flac"} or request.stream:
        raise HTTPException(400, "MiniMax Music 3 supports non-streaming audio output.")
    if generation_lock.locked():
        raise HTTPException(409, "Another song is currently being generated.")
    if not runtime.is_ready:
        runtime.start_loading()
        raise HTTPException(503, "The model is loading. Watch setup progress and try again when it is ready.")
    duration_seconds = request.max_new_tokens / 25
    profile = hardware_profile()
    if duration_seconds > profile["max_duration_seconds"]:
        raise HTTPException(
            400,
            f"This GPU profile is limited to {profile['max_duration_seconds']} seconds to prevent CUDA out-of-memory errors.",
        )
    output_path = OUTPUTS / f"legacy-music-{uuid.uuid4().hex[:10]}.flac"

    def run():
        with generation_lock:
            runtime.generate(
                lyrics=request.input,
                prompt=request.instructions,
                duration_seconds=duration_seconds,
                seed=request.seed,
                output_path=output_path,
            )
            first_line = next(
                (line.strip() for line in request.input.splitlines() if line.strip() and not line.strip().startswith("[")),
                "Untitled Legacy Track",
            )
            metadata = {
                "id": output_path.stem,
                "title": first_line[:72],
                "seed": request.seed,
                "duration_seconds": round(duration_seconds, 2),
                "lyrics": request.input,
                "instructions": request.instructions,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                output_path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            except OSError:
                pass

    try:
        await asyncio.to_thread(run)
    except RuntimeError as exc:
        raise HTTPException(500, str(exc)) from exc
    return FileResponse(output_path, media_type="audio/flac", filename=output_path.name)


app.mount("/outputs", StaticFiles(directory=OUTPUTS), name="outputs")
app.mount("/", StaticFiles(directory=ROOT / "static", html=True), name="dashboard")
