# Run EyeSense backend and frontend from PowerShell
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

Write-Host "Starting EyeSense Backend (uvicorn) on http://127.0.0.1:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend.main:app --reload --port 8000"
Start-Sleep -Seconds 3
Write-Host "Starting Streamlit frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run .\frontend\app.py"
Write-Host "Both processes started."