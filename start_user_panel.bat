@echo off
title Trendyol Bot - Kullanici Paneli

echo ================================================
echo Trendyol Bot - Kullanici Paneli Baslatiliyor
echo ================================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    echo Lutfen Python'u yukleyin: https://python.org
    pause
    exit /b 1
)

REM Sanal ortam kontrolu
if not exist ".venv" (
    echo Sanal ortam olusturuluyor...
    python -m venv .venv
)

REM Sanal ortami aktif et
call .venv\Scripts\activate.bat

REM Gereksinimleri yukle
echo Gereksinimler kontrol ediliyor...
pip install -r requirements.txt

REM .env dosyasi kontrolu
if not exist ".env" (
    echo UYARI: .env dosyasi bulunamadi!
    echo .env.example dosyasini .env olarak kopyalayin ve duzenleyin.
    echo.
    echo Discord OAuth ayarlarini yapmak icin:
    echo 1. https://discord.com/developers/applications adresine gidin
    echo 2. Yeni uygulama olusturun
    echo 3. OAuth2 bolumunden Client ID ve Client Secret alin
    echo 4. Redirect URI: http://localhost:5001/auth/callback
    echo.
    pause
    exit /b 1
)

REM Kullanici panelini baslat
echo.
echo Kullanici paneli baslatiliyor...
echo Tarayicinizda http://localhost:5001 adresini acin
echo.
python start_user_panel.py

pause