@echo off
setlocal
cd /d "%~dp0"

echo === Screen ESP - one-click build ===
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH. Install Python 3.10 or 3.11 from python.org first,
    echo making sure to check "Add python.exe to PATH" during install, then run this again.
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies (this can take a few minutes)...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo [4/5] Downloading YOLO model weights...
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

echo [5/5] Building ScreenESP.exe...
pyinstaller --name ScreenESP --onedir --console --collect-all mediapipe --collect-all ultralytics --collect-all torch --add-data "yolov8n.pt;." main.py

echo.
if exist dist\ScreenESP\ScreenESP.exe (
    echo SUCCESS. Your exe is at: dist\ScreenESP\ScreenESP.exe
    echo IMPORTANT: keep it inside the ScreenESP folder - it needs the files next to it.
    echo Also install the Visual C++ Redistributable if you haven't:
    echo https://aka.ms/vs/17/release/vc_redist.x64.exe
) else (
    echo Something went wrong - scroll up to see the error above.
)
pause
