@echo off
setlocal
cd /d "%~dp0"
title Legacy Music Studio - Setup
echo.
echo  LEGACY MUSIC STUDIO - FIRST TIME SETUP
echo  ---------------------------------------
where py >nul 2>nul || (echo Python 3.12 is required. Install it from python.org and enable Add Python to PATH.& pause & exit /b 1)
if not exist .venv py -3.12 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
echo Installing CUDA-enabled PyTorch...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
echo Installing MiniMax Music 3 dependencies...
pip install -r requirements.txt
pip install "git+https://github.com/huggingface/diffusers@dafe3733fcfdbf3c48915fe77be3aef65b5d6a2d"
echo.
echo Setup complete. Run launch_windows.bat.
pause
