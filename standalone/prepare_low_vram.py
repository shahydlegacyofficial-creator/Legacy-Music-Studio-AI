from __future__ import annotations

import sys
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parent
COMFY = ROOT / "ComfyUI"
REPO = "Comfy-Org/MiniMax-Music-3"
FILES = (
    "diffusion_models/minimax_music3_dit_int8_convrot.safetensors",
    "text_encoders/minimax_music3_text_encoder_pruned_int8_convrot.safetensors",
    "vae/minimax_music3_dav.safetensors",
)


def main():
    if not (COMFY / "main.py").is_file():
        raise RuntimeError("ComfyUI was not downloaded correctly.")
    models = COMFY / "models"
    for filename in FILES:
        print(f"Downloading {filename} (existing partial files will resume)...")
        hf_hub_download(repo_id=REPO, filename=filename, local_dir=models)

    print("Ready: the Legacy dashboard will control MiniMax through the local engine API.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
