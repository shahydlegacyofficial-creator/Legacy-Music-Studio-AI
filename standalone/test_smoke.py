import json
import unittest
from pathlib import Path

from comfy_runtime import ComfyUIRuntime


ROOT = Path(__file__).resolve().parent


class StandaloneSmokeTests(unittest.TestCase):
    def test_runtime_reports_engine_starting_when_offline(self):
        runtime = ComfyUIRuntime("http://127.0.0.1:1")
        status = runtime.status()
        self.assertEqual(status["state"], "loading")
        self.assertTrue(status["low_vram"])

    def test_dashboard_has_required_controls(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
        api = (ROOT / "app.py").read_text(encoding="utf-8")
        for marker in ("/api/setup", "/api/status", "/api/hardware", "/api/library", "/v1/audio/speech", "GENERATE TRACK", "DOWNLOAD LOSSLESS FLAC"):
            self.assertIn(marker, html + script + api)
        for marker in ('data-duration="15"', 'data-duration="30"', 'data-duration="60"', 'data-duration="120"', "page-library", "page-presets", "page-engine"):
            self.assertIn(marker, html)
        for marker in ("Modern Pop Anthem", "Modern Arena Rock", "K-Pop Neon Rush", "Velvet R&B", "Lo-Fi Study Tape", "Afrobeats Sunset"):
            self.assertIn(marker, script)
        self.assertIn('total_mb >= 22_000', api)
        self.assertIn('total_mb >= 14_000', api)
        self.assertIn("REMIX ↻", script)
        self.assertIn("textarea{font-size:12px;line-height:1.8}", styles)
        self.assertIn(".nav-item b{font-size:11.5px}", styles)

    def test_windows_entrypoints_exist(self):
        self.assertTrue((ROOT / "setup_windows.bat").is_file())
        self.assertTrue((ROOT / "launch_windows.bat").is_file())
        self.assertTrue((ROOT / "START_HERE_LOW_VRAM.bat").is_file())
        self.assertTrue((ROOT / "setup_low_vram_windows.bat").is_file())
        self.assertTrue((ROOT / "launch_low_vram_windows.bat").is_file())
        self.assertTrue((ROOT / "start_legacy.py").is_file())

    def test_low_vram_dependencies_are_installed(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        launcher = (ROOT / "launch_windows.bat").read_text(encoding="utf-8")
        for package in ("accelerate", "transformers", "safetensors"):
            self.assertIn(package, requirements)
            self.assertIn(package, launcher)

    def test_api_prompt_uses_int8_and_tiled_decode(self):
        runtime = ComfyUIRuntime()
        classes = {
            "UNETLoader": {"unet_name": [[runtime.UNET]], "weight_dtype": [["default"]]},
            "CLIPLoader": {"clip_name": [[runtime.CLIP]], "type": [["minimax"]], "device": [["default"]]},
            "VAELoader": {"vae_name": [[runtime.VAE]]},
            "MiniMaxMusic3TextEncode": {"clip": ["CLIP"], "caption": ["STRING"], "lyrics": ["STRING"], "seed": ["INT"], "max_duration": ["FLOAT"], "temperature": ["FLOAT", {"default": 1.7}], "top_k": ["INT", {"default": 50}]},
            "ConditioningZeroOut": {"conditioning": ["CONDITIONING"]},
            "EmptyMiniMaxMusic3LatentAudio": {"seconds": ["FLOAT"], "batch_size": ["INT", {"default": 1}]},
            "KSampler": {"model": ["MODEL"], "positive": ["CONDITIONING"], "negative": ["CONDITIONING"], "latent_image": ["LATENT"], "seed": ["INT"], "steps": ["INT"], "cfg": ["FLOAT"], "sampler_name": [["euler"]], "scheduler": [["simple"]], "denoise": ["FLOAT"]},
            "VAEDecodeAudioTiled": {"samples": ["LATENT"], "vae": ["VAE"], "tile_size": ["INT"], "overlap": ["INT"]},
            "SaveAudio": {"audio": ["AUDIO"], "filename_prefix": ["STRING"]},
        }
        runtime._object_info = {name: {"input": {"required": inputs}} for name, inputs in classes.items()}
        prompt = runtime.build_prompt(lyrics="[Verse]\nHello", prompt="Rock", duration_seconds=15, seed=7)
        self.assertEqual(prompt["1"]["inputs"]["unet_name"], runtime.UNET)
        self.assertEqual(prompt["8"]["class_type"], "VAEDecodeAudioTiled")
        self.assertEqual(prompt["9"]["class_type"], "SaveAudio")
        self.assertNotIn("quality", prompt["9"]["inputs"])

    def test_low_vram_installer_uses_official_int8_files(self):
        helper = (ROOT / "prepare_low_vram.py").read_text(encoding="utf-8")
        launcher = (ROOT / "launch_low_vram_windows.bat").read_text(encoding="utf-8")
        for marker in (
            "Comfy-Org/MiniMax-Music-3",
            "minimax_music3_dit_int8_convrot.safetensors",
            "minimax_music3_text_encoder_pruned_int8_convrot.safetensors",
            "minimax_music3_dav.safetensors",
        ):
            self.assertIn(marker, helper)
        supervisor = (ROOT / "start_legacy.py").read_text(encoding="utf-8")
        self.assertIn("--lowvram", supervisor)
        self.assertIn("expandable_segments:True", supervisor)
        self.assertIn("127.0.0.1:8787", supervisor)
        self.assertIn("process.poll()", supervisor)
        self.assertNotIn("powershell", launcher.lower())
        self.assertIn("from huggingface_hub import is_offline_mode", launcher)
        self.assertIn("--upgrade transformers huggingface-hub", launcher)
        low_requirements = (ROOT / "requirements_low_vram.txt").read_text(encoding="utf-8")
        self.assertNotIn("huggingface-hub==0.34.4", low_requirements)
        self.assertNotIn('start ^"^" ^"http://127.0.0.1:8188', launcher)


if __name__ == "__main__":
    unittest.main()
