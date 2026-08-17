@echo off
setlocal
cd /d "%~dp0"
title Legacy Music Studio - Low VRAM
if not exist ComfyUI\main.py (
  echo The low-VRAM engine needs to be installed first.
  call setup_low_vram_windows.bat
  if errorlevel 1 exit /b 1
)
if not exist .comfy-venv\Scripts\python.exe (
  call setup_low_vram_windows.bat
  if errorlevel 1 exit /b 1
)
call launch_low_vram_windows.bat
