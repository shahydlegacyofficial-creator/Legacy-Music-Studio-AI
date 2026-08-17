from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


class ComfyUIRuntime:
    """Small API client that keeps ComfyUI hidden behind the Legacy dashboard."""

    UNET = "minimax_music3_dit_int8_convrot.safetensors"
    CLIP = "minimax_music3_text_encoder_pruned_int8_convrot.safetensors"
    VAE = "minimax_music3_dav.safetensors"

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")).rstrip("/")
        self._object_info: dict | None = None
        self.last_error: str | None = None

    def _request(self, path: str, *, data: dict | None = None, timeout: float = 10):
        body = None if data is None else json.dumps(data).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": "Legacy-Music-Studio/1.4"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get_content_type()
            payload = response.read()
        return json.loads(payload) if content_type == "application/json" else payload

    @property
    def is_ready(self) -> bool:
        try:
            self._request("/system_stats", timeout=2)
            return True
        except (OSError, urllib.error.URLError, ValueError):
            return False

    def status(self):
        if self.is_ready:
            self.last_error = None
            return {
                "state": "ready",
                "detail": "MiniMax Music 3 INT8 engine ready · Legacy dashboard",
                "progress": 100,
                "error": None,
                "low_vram": True,
            }
        return {
            "state": "loading",
            "detail": "Starting the hidden MiniMax INT8 engine…",
            "progress": 45,
            "error": self.last_error,
            "low_vram": True,
        }

    def start_loading(self):
        # The Windows launcher owns the engine process; this endpoint is retained
        # for compatibility with the existing dashboard setup button.
        return self.status()

    def _schemas(self) -> dict:
        if self._object_info is None:
            self._object_info = self._request("/object_info", timeout=30)
        return self._object_info

    def _inputs(self, class_type: str, overrides: dict) -> dict:
        """Fill required Comfy inputs from its live schema, preserving links."""
        schema = self._schemas().get(class_type)
        if not schema:
            raise RuntimeError(f"The installed ComfyUI does not provide {class_type}. Run setup again to update it.")
        definitions = {}
        for group in ("required", "optional"):
            definitions.update(schema.get("input", {}).get(group, {}))
        result = {name: value for name, value in overrides.items() if name in definitions}
        for name, spec in schema.get("input", {}).get("required", {}).items():
            if name in result:
                continue
            # Newer ComfyUI schema versions namespace inputs belonging to a
            # dynamic widget, e.g. ``format.quality`` instead of ``quality``.
            # Accept the stable leaf name so the bridge works with both forms.
            leaf_name = name.rsplit(".", 1)[-1]
            if leaf_name in overrides:
                result[name] = overrides[leaf_name]
                continue
            kind = spec[0] if isinstance(spec, list) and spec else None
            options = spec[1] if isinstance(spec, list) and len(spec) > 1 and isinstance(spec[1], dict) else {}
            if "default" in options:
                result[name] = options["default"]
            elif isinstance(kind, list) and kind:
                result[name] = kind[0]
            else:
                raise RuntimeError(f"ComfyUI requires an unsupported {class_type}.{name} input.")
        return result

    def build_prompt(self, *, lyrics: str, prompt: str, duration_seconds: float, seed: int) -> dict:
        nodes = {
            "1": {"class_type": "UNETLoader", "inputs": self._inputs("UNETLoader", {
                "unet_name": self.UNET, "weight_dtype": "default"
            })},
            "2": {"class_type": "CLIPLoader", "inputs": self._inputs("CLIPLoader", {
                "clip_name": self.CLIP, "type": "minimax", "device": "default"
            })},
            "3": {"class_type": "VAELoader", "inputs": self._inputs("VAELoader", {"vae_name": self.VAE})},
            "4": {"class_type": "MiniMaxMusic3TextEncode", "inputs": self._inputs(
                "MiniMaxMusic3TextEncode",
                {"clip": ["2", 0], "caption": prompt, "lyrics": lyrics, "seed": seed,
                 "max_duration": float(duration_seconds), "temperature": 1.7, "top_k": 50},
            )},
            "5": {"class_type": "ConditioningZeroOut", "inputs": self._inputs(
                "ConditioningZeroOut", {"conditioning": ["4", 0]}
            )},
            "6": {"class_type": "EmptyMiniMaxMusic3LatentAudio", "inputs": self._inputs(
                "EmptyMiniMaxMusic3LatentAudio", {"seconds": ["4", 1], "batch_size": 1}
            )},
            "7": {"class_type": "KSampler", "inputs": self._inputs("KSampler", {
                "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0],
                "latent_image": ["6", 0], "seed": seed, "steps": 30, "cfg": 1.7,
                "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
            })},
            "8": {"class_type": "VAEDecodeAudioTiled", "inputs": self._inputs(
                "VAEDecodeAudioTiled", {"samples": ["7", 0], "vae": ["3", 0], "tile_size": 1536, "overlap": 64}
            )},
            "9": {"class_type": "SaveAudio", "inputs": self._inputs(
                "SaveAudio", {"audio": ["8", 0], "filename_prefix": "LegacyMusic/track"}
            )},
        }
        return nodes

    @staticmethod
    def _find_audio(history: dict) -> dict | None:
        for output in history.get("outputs", {}).values():
            for key in ("audio", "audios", "files"):
                files = output.get(key, []) if isinstance(output, dict) else []
                if files:
                    return files[0]
        return None

    def generate(self, *, lyrics: str, prompt: str, duration_seconds: float, seed: int, output_path: Path):
        if not self.is_ready:
            raise RuntimeError("The hidden MiniMax engine is not running. Close this window and use START_HERE_LOW_VRAM.bat.")
        client_id = uuid.uuid4().hex
        try:
            queued = self._request("/prompt", data={
                "prompt": self.build_prompt(lyrics=lyrics, prompt=prompt, duration_seconds=duration_seconds, seed=seed),
                "client_id": client_id,
            }, timeout=60)
            if "prompt_id" not in queued:
                raise RuntimeError(queued.get("error", "ComfyUI rejected the generation workflow."))
            prompt_id = queued["prompt_id"]
            deadline = time.monotonic() + float(os.getenv("LEGACY_MUSIC_TIMEOUT", "7200"))
            while time.monotonic() < deadline:
                entry = self._request(f"/history/{urllib.parse.quote(prompt_id)}", timeout=30).get(prompt_id)
                if entry:
                    audio = self._find_audio(entry)
                    if audio:
                        query = urllib.parse.urlencode({
                            "filename": audio["filename"], "subfolder": audio.get("subfolder", ""),
                            "type": audio.get("type", "output"),
                        })
                        payload = self._request(f"/view?{query}", timeout=300)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_bytes(payload)
                        return output_path
                    status = entry.get("status", {})
                    if status.get("completed"):
                        messages = status.get("messages", [])
                        raise RuntimeError(f"ComfyUI finished without an audio file. {messages[-1] if messages else ''}")
                time.sleep(2)
            raise RuntimeError("Generation timed out after two hours.")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"ComfyUI API error ({exc.code}): {detail[:1200]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError("The hidden MiniMax engine stopped responding. Restart START_HERE_LOW_VRAM.bat.") from exc
