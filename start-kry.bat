
@echo off
echo Starting Kry...

REM Start FastAPI backend
start "Kry Backend" /D "%~dp0" cmd /k ".venv\Scripts\python.exe -m uvicorn api:app --reload"

REM Start React frontend
start "Kry Frontend" /D "%~dp0frontend" cmd /k "npm.cmd run dev"

REM Wait for servers to start
timeout /t 5 /nobreak >nul

REM Open website
start "" "http://localhost:5173"

echo Kry started!
