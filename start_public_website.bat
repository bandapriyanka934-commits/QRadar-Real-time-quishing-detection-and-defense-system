@echo off
title QRadar Public Web Server & Phone Link
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py start_public_website.py
) else (
    python start_public_website.py
)
pause
