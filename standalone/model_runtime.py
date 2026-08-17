from __future__ import annotations

import os
import threading
import traceback
from pathlib import Path


class MiniMaxRuntime:
    def __init__(self):
        self.pipe = None
        self.state = "not_loaded"
        self.detail = "Model files have not been loaded yet."
        self.progress = 0
        self.error = None
        self._load_lock = threading.Lock()

    @property
    def is_ready(self):
        return self.state == "ready" and self.pipe is not None

    def status(self):
        return {
            "state": self.state,
            "detail": self.detail,
            "progress": self.progress,
            "error": self.error,
            "low_vram": os.getenv("LEGACY_MUSIC_LOW_VRAM", "1") != "0",
        }

    def start_loading(self):
        if self.state in {"loading", "ready"}:
            return
        threading.Thread(target=self._load, daemon=True, name="minimax-loader").start()

    @staticmethod
    def _load_and_resolve_language_model(pipe, manager, dtype):
        """Load modular components and return the actual language-model module.

        Newer ModularPipeline builds use ``torch_dtype``. The MiniMax preview
        commit also accepted ``dtype``. Supporting both prevents a silent empty
        component on mismatched Diffusers builds.
        """
        try:
            pipe.load_components(torch_dtype=dtype)
        except TypeError as exc:
            if "torch_dtype" not in str(exc):
                raise
            pipe.load_components(dtype=dtype)

        language_model = getattr(pipe, "language_model", None)
        if language_model is None:
            components = getattr(pipe, "components", None)
            if isinstance(components, dict):
                language_model = components.get("language_model")
        if language_model is None and hasattr(manager, "get_one"):
            try:
                language_model = manager.get_one(name="language_model")
            except (KeyError, ValueError):
                language_model = None
        if language_model is None:
            available = []
            registered = getattr(manager, "components", {})
            if isinstance(registered, dict):
                available = sorted(str(name) for name in registered)
            suffix = f" Registered components: {', '.join(available)}" if available else ""
            raise RuntimeError(
                "Diffusers did not load the MiniMax language_model component. "
                "Run setup_windows.bat again to reinstall the supported Diffusers build."
                + suffix
            )
        return language_model

    def _load(self):
        if not self._load_lock.acquire(blocking=False):
            return
        try:
            self.state, self.progress = "loading", 5
            self.detail = "Checking CUDA and loading model components…"
            import torch
            from diffusers import ComponentsManager, ModularPipeline
            from diffusers.hooks import apply_group_offloading

            if not torch.cuda.is_available():
                raise RuntimeError("CUDA is unavailable. Install the NVIDIA driver and CUDA-enabled PyTorch.")
            self.progress = 15
            self.detail = f"GPU detected: {torch.cuda.get_device_name(0)}"
            manager = ComponentsManager()
            manager.enable_auto_cpu_offload(device="cuda")
            self.progress = 25
            self.detail = "Downloading or reading MiniMax Music 3 weights…"
            cache_dir = os.getenv("HF_HOME")
            kwargs = {"components_manager": manager}
            if cache_dir:
                kwargs["cache_dir"] = cache_dir
            pipe = ModularPipeline.from_pretrained("MiniMaxAI/MiniMax-Music3", **kwargs)
            self.progress = 70
            self.detail = "Preparing BF16 components…"
            language_model = self._load_and_resolve_language_model(pipe, manager, torch.bfloat16)
            if os.getenv("LEGACY_MUSIC_LOW_VRAM", "1") != "0":
                self.detail = "Enabling 8 GB low-VRAM layer streaming…"
                apply_group_offloading(
                    language_model,
                    onload_device=torch.device("cuda"),
                    offload_type="leaf_level",
                    use_stream=True,
                )
            else:
                pipe.to("cuda")
            self.pipe = pipe
            self.progress = 100
            self.state = "ready"
            self.detail = f"Ready on {torch.cuda.get_device_name(0)}"
            self.error = None
        except Exception as exc:
            self.state = "error"
            self.detail = "Model setup failed."
            self.error = f"{exc}\n\n{traceback.format_exc(limit=3)}"
        finally:
            self._load_lock.release()

    def generate(self, *, lyrics: str, prompt: str, duration_seconds: float, seed: int, output_path: Path):
        if not self.is_ready:
            raise RuntimeError("The model is not ready.")
        try:
            import soundfile as sf
            import torch

            generator = torch.Generator("cuda").manual_seed(seed)
            audio = self.pipe(
                prompt=prompt,
                lyrics=lyrics,
                audio_duration=float(duration_seconds),
                generator=generator,
                output="audios",
            )[0]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(output_path, audio.T.float().cpu().numpy(), self.pipe.sampling_rate)
        except torch.cuda.OutOfMemoryError as exc:
            torch.cuda.empty_cache()
            raise RuntimeError("GPU memory ran out. Restart the app and try a shorter duration.") from exc
        except Exception as exc:
            raise RuntimeError(f"Generation failed: {exc}") from exc
