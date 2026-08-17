@echo off
setlocal
cd /d "%~dp0"
title Legacy Music Studio
if not exist .comfy-venv\Scripts\python.exe (
  echo Low-VRAM setup is incomplete.
  call setup_low_vram_windows.bat
  if errorlevel 1 exit /b 1
)
.comfy-venv\Scripts\python.exe -c "import fastapi, uvicorn" >nul 2>nul
if errorlevel 1 (
  echo Updating the Legacy dashboard components...
  .comfy-venv\Scripts\python.exe -m pip install -r requirements_low_vram.txt
  if errorlevel 1 (echo Dashboard dependency update failed.& pause & exit /b 1)
)
.comfy-venv\Scripts\python.exe -c "from huggingface_hub import is_offline_mode; from transformers import CLIPTokenizer" >nul 2>nul
if errorlevel 1 (
  echo Repairing the ComfyUI and Transformers dependency versions...
  .comfy-venv\Scripts\python.exe -m pip install --upgrade transformers huggingface-hub
  if errorlevel 1 (echo ComfyUI dependency repair failed.& pause & exit /b 1)
)
echo.
.comfy-venv\Scripts\python.exe start_legacy.py
pause
