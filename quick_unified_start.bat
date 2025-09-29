@echo off
chcp 65001 >nul
title Trendyol Bot - Unified Web App (Quick Start)

echo ================================
echo 🚀 TRENDYOL BOT - UNIFIED WEB APP
echo ================================
echo.

:: UTF-8 encoding ayarla
set PYTHONUTF8=1

:: Sanal ortamı kontrol et ve aktifleştir
echo 📦 Python ortamı hazırlanıyor...
if exist .venv\Scripts\activate.bat (
    echo ✅ Sanal ortam bulundu, aktifleştiriliyor...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  Sanal ortam bulunamadı, sistem Python kullanılıyor...
)

:: Gerekli paketleri kontrol et
echo 📋 Gereksinimler kontrol ediliyor...
python -c "import flask, flask_cors, flask_socketio, cryptography" 2>nul
if errorlevel 1 (
    echo 📦 Eksik paketler yükleniyor...
    pip install flask flask-cors flask-socketio cryptography python-dotenv requests
)

:: .env dosyasını kontrol et
if not exist .env (
    echo 📄 .env dosyası oluşturuluyor...
    copy .env.example .env >nul 2>&1
    if not exist .env (
        echo WEB_PORT=5000 > .env
        echo WEB_HOST=0.0.0.0 >> .env
        echo ADMIN_SECRET_KEY=admin123 >> .env
        echo FLASK_SECRET_KEY=unified-secret-key-2024 >> .env
    )
)

:: Veritabanını kontrol et
if not exist data (
    echo 📁 Data klasörü oluşturuluyor...
    mkdir data
)

if not exist data\trendyol_bot.db (
    echo 🗄️  Veritabanı oluşturuluyor...
    python -c "from database import Database; db = Database(); db.close(); print('✅ Veritabanı oluşturuldu')"
)

:: Port kontrolü
echo 🔍 Port 5000 kontrol ediliyor...
netstat -an | find "0.0.0.0:5000" >nul
if not errorlevel 1 (
    echo ⚠️  Port 5000 kullanımda, alternatif port deneniyor...
    set WEB_PORT=5001
) else (
    set WEB_PORT=5000
)

echo.
echo 🌍 Unified Web App başlatılıyor...
echo 📱 Yerel erişim: http://localhost:%WEB_PORT%
echo.
echo 🔗 GİRİŞ LİNKLERİ:
echo 👨‍💼 Admin: http://localhost:%WEB_PORT%/login?type=admin
echo 👤 User: http://localhost:%WEB_PORT%/login?type=user
echo.
echo ⚠️  Admin Anahtarı: admin123 (güvenlik için değiştirin!)
echo.

:: Tarayıcıyı aç (opsiyonel)
timeout /t 3 /nobreak >nul
start http://localhost:%WEB_PORT%

:: Uygulamayı başlat
python unified_web_app.py

echo.
echo 🛑 Uygulama durduruldu.
pause