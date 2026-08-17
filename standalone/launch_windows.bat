@echo off
setlocal
cd /d "%~dp0"
title Legacy Music Studio
if not exist .venv\Scripts\python.exe (
  echo First-time setup has not been completed.
  call setup_windows.bat
)
.venv\Scripts\python.exe -c "import accelerate, transformers, safetensors" >nul 2>nul
if errorlevel 1 (
  echo Repairing missing MiniMax dependencies...
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Dependency repair failed. Run setup_windows.bat again.
    pause
    exit /b 1
  )
)
set LEGACY_MUSIC_LOW_VRAM=1
set HF_HOME=%~dp0model-cache
if not exist outputs mkdir outputs
start "" cmd /c "timeout /t 3 /nobreak ^>nul ^& start ^"^" ^"http://127.0.0.1:8787^""
.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8787
pause
