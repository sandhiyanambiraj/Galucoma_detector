@echo off
echo Starting EyeSense AI Application...
echo.
REM Change directory to the script's directory to ensure imports work
cd /d %~dp0

echo Starting Backend API (uvicorn)...
start "EyeSense Backend" cmd /k "uvicorn backend.main:app --reload --port 8000"

echo Waiting for backend to start...
timeout /t 3

echo Starting Frontend (Streamlit)...
start "EyeSense Frontend" cmd /k "streamlit run .\frontend\app.py"

echo Done. Two windows should be open: Backend and Frontend.
