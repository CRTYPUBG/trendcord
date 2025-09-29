@echo off
title LocalTunnel Quick Setup

echo Checking Node.js...
node --version
if errorlevel 1 (
    echo Node.js not found! Please install from https://nodejs.org
    pause
    exit /b 1
)

echo Installing LocalTunnel...
npm install -g localtunnel

echo Starting tunnels...

REM Ana Panel
start "Main Panel" cmd /k "echo Main Panel Tunnel && lt --port 5000"

REM Kullanici Paneli  
start "User Panel" cmd /k "echo User Panel Tunnel && lt --port 8080"

echo.
echo Tunnels started! Check the opened windows for URLs.
echo.
pause