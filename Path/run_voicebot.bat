@echo off
title Sankar Group Voice Bot Launcher

echo ===================================================
echo   LAUNCHING SANKAR GROUP HYBRID VOICE BOT (PORT 1000)
echo ===================================================

:: 1. Launch the FastAPI Backend Server
echo Starting Python FastAPI backend...
start cmd /k "cd /d C:\Projects\VoiceBot\Path && python main.py"

:: 2. Wait 3 seconds for the backend to initialize safely
timeout /t 3 /nobreak >nul

:: 3. Launch the ngrok tunnel on Port 1000
echo Starting ngrok tunnel on port 1000...
start cmd /k "ngrok http 1000"

echo ===================================================
echo   Both services are starting up in separate windows!
echo ===================================================
pause