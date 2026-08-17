# Legacy Music Studio AI

**A private, local-first AI music workstation for Windows.**

Legacy Music Studio AI turns lyrics and structured creative direction into vocal
and instrumental music through a polished creator-focused dashboard. The Windows
application runs MiniMax Music 3 locally through a hidden ComfyUI engine, keeping
lyrics and generated audio on the creator's computer and avoiding per-track API
fees.

This repository contains the complete **Build 3.0** source for both the Windows
studio and its hosted companion dashboard.

## Highlights

- Lyrics-to-music generation with structured genre, mood, vocal and arrangement control
- 20 curated genre systems including Pop, Rock, K-Pop, R&B, Lo-Fi, Metal, EDM,
  Afrobeats, Reggae, Trap, Funk, Techno and cinematic scoring
- Searchable preset library with category filters
- Automatic NVIDIA GPU and VRAM detection
- Hardware-aware duration controls that protect lower-memory GPUs
- Lossless FLAC export and repeatable generation seeds
- Local track archive with one-click Remix workflow
- Autosaved drafts and engine telemetry
- Hidden ComfyUI integration: users work entirely inside the Legacy dashboard
- Responsive hosted companion built with React and Next.js

## Hardware profiles

| GPU memory | Available duration | Profile |
| --- | ---: | --- |
| 8 GB | 15–30 seconds | Protected low-VRAM mode |
| 16 GB or more | Up to 60 seconds | Extended mode |
| 24 GB or more | Up to 2 minutes | Experimental extended mode |

Longer tracks require more GPU memory. Close games and GPU-heavy creative
applications before loading the local model.

## Repository structure

```text
app/                 Hosted companion interface
worker/              Cloudflare-compatible application entry point
scripts/             Hosted build and validation scripts
standalone/          Windows application and local MiniMax runtime
standalone/static/   Local dashboard interface
tests/               Hosted interface checks
```

## Windows quick start

### Requirements

- Windows 11
- Python 3.12 with **Add Python to PATH** enabled
- Git for Windows
- Current NVIDIA driver and a CUDA-capable NVIDIA GPU
- At least 65 GB of free disk space for downloaded model files
- Internet access for the initial setup

### Run the 8 GB low-VRAM build

1. Download or clone this repository.
2. Open the `standalone` folder.
3. Double-click `START_HERE_LOW_VRAM.bat`.
4. Allow the first-run setup to install ComfyUI and download the model files.
5. Keep the launcher window open while generating.
6. Begin with a 15-second generation to confirm the GPU configuration.

The dashboard opens at `http://127.0.0.1:8787`. Generated audio and metadata are
stored inside `standalone/outputs` and are intentionally ignored by Git.

For more Windows setup and troubleshooting information, read
[`standalone/README.md`](standalone/README.md).

## Hosted companion development

### Requirements

- Node.js 22.13 or newer
- npm

### Local development

```bash
npm ci
npm run dev
```

### Validation

```bash
npm run lint
npm test
```

The hosted interface is a companion to the Windows runtime. Music generation
still happens on the user's NVIDIA GPU through the local application.

## Privacy

The Windows workflow is local-first. Lyrics, prompts and generated tracks stay
on the user's PC unless the user chooses to upload or share them elsewhere.

## Models and third-party software

Model weights, ComfyUI, CUDA, Python environments and generated audio are **not
included in this repository**. The setup scripts download required third-party
components from their original sources.

MiniMax Music 3 must remain visibly credited in products that use it and remains
subject to the upstream MiniMax-Music3 license and acceptable-use requirements.
See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) before distributing or
commercializing the application.

## Commercial project status

Legacy Music Studio AI is a working, bootstrapped MVP designed for desktop
licensing, studio packages or expansion into a hybrid cloud subscription. The
original interface, application code, preset system and product documentation
are maintained by Shahyd Legacy.

## License

The original Legacy Music Studio AI source and brand assets are proprietary and
all rights are reserved. See [`LICENSE`](LICENSE). Third-party software and model
components retain their respective upstream licenses.
