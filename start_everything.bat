@echo off
title Trendyol Bot - Complete Setup

REM UTF-8 encoding aktif et
set PYTHONUTF8=1
chcp 65001 >nul

echo Starting everything...

REM Kullanici panelini baslat
echo Starting user panel on port 8080...
start "User Panel" cmd /k "python minimal_panel.py"

REM 5 saniye bekle
timeout /t 5 /nobreak

REM Ngrok tunnel baslat
echo Starting ngrok tunnel...
start "Ngrok Tunnel" cmd /k "ngrok http 8080"

echo.
echo Everything started!
echo - User Panel: http://localhost:8080
echo - Ngrok Tunnel: Check the ngrok window for URL
echo.
pause