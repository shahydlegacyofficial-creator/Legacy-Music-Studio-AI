# Legacy Music Studio — Windows standalone

Local MiniMax Music 3 dashboard for NVIDIA CUDA computers.

## Recommended for an 8 GB GPU

Run `START_HERE_LOW_VRAM.bat`. This installs the official ComfyUI MiniMax Music
3 INT8 diffusion model, pruned INT8 text encoder, and VAE. ComfyUI then runs as
a hidden low-memory engine while the Legacy Music Studio dashboard opens at
`http://127.0.0.1:8787`. You do not need to use or open the ComfyUI interface.

This is still MiniMax Music 3; it uses quantized weights rather than a different
music model. The older `launch_windows.bat` Diffusers route is intended for
larger GPUs and may exhaust an 8 GB card during model setup.

## Requirements

- Windows 11
- Python 3.12 (with **Add Python to PATH** enabled)
- Current NVIDIA driver
- NVIDIA CUDA-capable GPU; 8 GB VRAM is the minimum low-memory target
- At least 65 GB free disk space for model files and additional space for outputs
- Internet access during initial setup and the first model load

## Start

1. For 8 GB VRAM, double-click `START_HERE_LOW_VRAM.bat` and follow the prompt.
2. For 24 GB+ VRAM, use `setup_windows.bat`, then `launch_windows.bat`.
3. The Legacy dashboard opens automatically at `http://127.0.0.1:8787`.
4. Keep the launcher window open while generating.
5. Start with a 15–30 second generation to verify the PC configuration.

If the hidden engine cannot start, the launcher now stops immediately and shows
the last engine messages instead of remaining on `Waiting for the engine`. The
complete startup log is also saved as `comfyui-engine.log`.

Build 1.6 repairs the `cannot import name 'is_offline_mode'` startup error. An
older dashboard dependency had downgraded Hugging Face Hub below the version
required by the current Transformers package. The launcher now detects and
repairs this mismatch automatically.

Build 1.8 removes `SaveAudioAdvanced` from API generation. The dashboard now
uses ComfyUI's basic lossless FLAC saver, eliminating the version-dependent
`quality` / `format.quality` validation input entirely.

If you installed an earlier build and saw `Make sure to install accelerate`,
run `setup_windows.bat` again. The launcher also checks and repairs this
dependency automatically.

Build 1.2 also fixes the `NoneType has no attribute named_modules` error caused
when a Diffusers modular build accepted the old `dtype` argument without
populating the MiniMax language model.

Songs are stored in the `outputs` folder. Low-VRAM model files are stored under `ComfyUI\\models`.

Build 2.0 introduces the Legacy AI visual system and the complete local studio:
GPU-safe 15/30-second controls, an auto-indexed track library, reusable sound
presets, autosaved drafts, generation metadata, and engine telemetry. These are
dashboard-only improvements; the working hidden ComfyUI generation path is unchanged.

Build 2.1 adds a full readability pass: larger editor copy, navigation, panel
titles, helper labels, library metadata, and engine telemetry at all screen sizes.

Build 3.0 expands the studio to 20 searchable genre systems, including modern
Pop, Rock, K-Pop, R&B, Lo-Fi, EDM, Afrobeats, Hip-Hop, acoustic, reggae, jazz
and funk. Library tracks can now be loaded back into Create as a remix. Duration
is hardware-aware: the proven 8 GB profile remains capped at 30 seconds, 60
seconds unlocks at 16 GB VRAM, and the experimental 2-minute option unlocks at
24 GB VRAM.

## Notes for the RTX 5060 Ti 8 GB

Low-VRAM layer streaming is enabled by default. It trades speed for memory. Close games, creative software, and other GPU-heavy applications before loading the model. A large Windows page file may be required with 32 GB system RAM.

This project uses MiniMax Music 3's official Diffusers modular pipeline and low-VRAM offloading pattern.
