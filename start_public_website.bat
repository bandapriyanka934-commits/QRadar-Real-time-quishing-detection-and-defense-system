@echo off
title QRadar Public Web Server
echo ===================================================
echo   Starting QRadar Backend & Cloudflare Public Link
echo ===================================================

cd /d "%~dp0\backend"
start "" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

timeout /t 3 /nobreak >nul

cd /d "%~dp0"
echo Starting Cloudflare Tunnel...
.\cloudflared.exe tunnel --url http://127.0.0.1:8000
