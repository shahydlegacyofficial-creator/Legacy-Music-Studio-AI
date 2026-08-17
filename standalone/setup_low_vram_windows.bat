@echo off
setlocal
cd /d "%~dp0"
title Legacy Music Studio - Low VRAM Setup
echo.
echo  LEGACY MUSIC STUDIO - MINIMAX MUSIC 3 INT8
echo  -------------------------------------------
echo  This installs the official ComfyUI low-VRAM runtime.
echo.
where py >nul 2>nul || (echo Python 3.12 is required.& pause & exit /b 1)
where git >nul 2>nul || (echo Git is required. Install Git for Windows first.& pause & exit /b 1)
if not exist ComfyUI\main.py git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git ComfyUI
if errorlevel 1 (echo ComfyUI download failed.& pause & exit /b 1)
if not exist .comfy-venv py -3.12 -m venv .comfy-venv
call .comfy-venv\Scripts\activate.bat
python -m pip install --upgrade pip
echo Installing CUDA-enabled PyTorch...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
if errorlevel 1 (echo PyTorch installation failed.& pause & exit /b 1)
echo Installing the latest ComfyUI requirements...
pip install -r ComfyUI\requirements.txt
pip install -r requirements_low_vram.txt
python -c "from huggingface_hub import is_offline_mode; from transformers import CLIPTokenizer" >nul 2>nul
if errorlevel 1 pip install --upgrade transformers huggingface-hub
if errorlevel 1 (echo ComfyUI dependency installation failed.& pause & exit /b 1)
echo Downloading the MiniMax Music 3 INT8 files...
python prepare_low_vram.py
if errorlevel 1 (echo Model download failed. Run this setup again to resume.& pause & exit /b 1)
echo.
echo Low-VRAM setup complete.
echo Run START_HERE_LOW_VRAM.bat to open Legacy Music Studio.
pause
