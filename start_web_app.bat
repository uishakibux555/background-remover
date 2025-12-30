@echo off
setlocal
title Background Remover Web App Launcher

echo ===================================================
echo   STARTING BACKGROUND REMOVER WEB APP
echo ===================================================

echo.
echo 1. Starting Backend Server (Python/FastAPI)...
start "Backend Server" /min cmd /k "py -3.13 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

echo 2. Starting Frontend Server (React/Vite)...
cd frontend
start "Frontend Server" /min cmd /k "npm run dev"
cd ..

echo.
echo Waiting for servers to initialize...
timeout /t 4 >nul

echo 3. Opening Browser...
start http://localhost:5173

echo.
echo ===================================================
echo   APP STARTED!
echo ===================================================
echo.
echo - Keep the two popup windows open (minimized is fine).
echo - To stop the app, close those windows.
echo.
pause
