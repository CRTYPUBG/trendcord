@echo off
title User Panel - UTF8 Mode

REM UTF-8 encoding aktif et
set PYTHONUTF8=1
chcp 65001 >nul

echo Starting User Panel with UTF-8 encoding...
echo.

REM Kullanici panelini baslat
python start_user_panel.py

pause