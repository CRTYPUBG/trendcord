@echo off
title TRENDYOL BOT - COMPLETE USER PANEL

REM UTF-8 encoding
set PYTHONUTF8=1
chcp 65001 >nul

echo.
echo ================================================
echo    TRENDYOL BOT - COMPLETE USER PANEL
echo ================================================
echo.

REM Gerekli kutuphaneleri yukle
echo Installing requirements...
pip install flask python-dotenv requests >nul 2>&1

echo.
echo Starting complete user panel...
echo - Auto installs requirements
echo - Starts Flask panel on port 8080
echo - Auto starts tunnel (ngrok or localtunnel)
echo - Opens browser automatically
echo - Shows tunnel URL when ready
echo.

python complete_user_panel.py

pause