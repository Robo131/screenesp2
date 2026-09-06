@echo off
REM Run this on Windows, inside your activated venv, after pip install -r requirements.txt
REM Produces dist\ScreenESP.exe (a single-file executable)

pip install pyinstaller

pyinstaller ^
  --name ScreenESP ^
  --onefile ^
  --noconsole ^
  --collect-all mediapipe ^
  --collect-all ultralytics ^
  --add-data "yolov8n.pt;." ^
  main.py

echo.
echo Build complete. Find it at dist\ScreenESP.exe
pause
