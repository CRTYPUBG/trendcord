@echo off
title Trendyol Bot - Kullanici Paneli (Hizli Baslangic)

echo ================================================
echo Trendyol Bot - Kullanici Paneli Hizli Baslangic
echo ================================================
echo.

REM Gerekli klasöre git
cd /d "%~dp0"

REM Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    pause
    exit /b 1
)

REM Gerekli kütüphaneleri yükle
echo Gereksinimler kontrol ediliyor...
pip install flask flask-cors flask-socketio cryptography requests python-dotenv

REM .env dosyasi kontrolu
if not exist ".env" (
    echo UYARI: .env dosyasi bulunamadi!
    echo .env.example dosyasini .env olarak kopyalayin.
    pause
    exit /b 1
)

REM Avatar test
echo.
echo Avatar URL testi yapiliyor...
python test_simple_avatar.py

echo.
echo OAuth ayarlari kontrol ediliyor...
python debug_oauth.py

echo.
echo Kullanici paneli baslatiliyor...
echo Tarayicinizda http://localhost:3000 adresini acin
echo.

python start_user_panel.py

pause