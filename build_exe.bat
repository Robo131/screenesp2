@echo off
REM Run this on Windows, inside your activated venv, after pip install -r requirements.txt
REM Produces dist\ScreenESP\ScreenESP.exe (a folder, not a single file -
REM onedir mode is far more reliable for PyTorch apps than onefile)

pip install pyinstaller

pyinstaller ^
  --name ScreenESP ^
  --onedir ^
  --console ^
  --collect-all mediapipe ^
  --collect-all ultralytics ^
  --collect-all torch ^
  --add-data "yolov8n.pt;." ^
  main.py

echo.
echo Build complete. Find it at dist\ScreenESP\ScreenESP.exe
echo IMPORTANT: keep ScreenESP.exe inside its ScreenESP folder - it needs the DLLs next to it.
pause
