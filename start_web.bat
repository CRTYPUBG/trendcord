@echo off
title TrendCord Web UI
color 0C

echo.
echo  ████████╗██████╗ ███████╗███╗   ██╗██████╗  ██████╗ ██████╗ ██████╗ 
echo  ╚══██╔══╝██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
echo     ██║   ██████╔╝█████╗  ██╔██╗ ██║██║  ██║██║     ██║   ██║██████╔╝
echo     ██║   ██╔══██╗██╔══╝  ██║╚██╗██║██║  ██║██║     ██║   ██║██╔══██╗
echo     ██║   ██║  ██║███████╗██║ ╚████║██████╔╝╚██████╗╚██████╔╝██║  ██║
echo     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
echo.
echo                         🌐 Web UI Başlatılıyor...
echo                         =========================
echo.

cd /d "%~dp0"

REM Virtual environment kontrolü
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment bulunamadı!
    echo 🔧 Lütfen önce install.bat scriptini çalıştırın.
    pause
    exit /b 1
)

REM .env dosyası kontrolü
if not exist ".env" (
    echo ❌ .env dosyası bulunamadı!
    echo 📝 Lütfen .env.example dosyasını .env olarak kopyalayın ve düzenleyin.
    pause
    exit /b 1
)

REM Virtual environment aktive et
echo 🔧 Virtual environment aktive ediliyor...
call venv\Scripts\activate.bat

REM Flask secret key kontrolü
findstr /C:"FLASK_SECRET_KEY=YOUR_FLASK_SECRET_KEY" .env >nul
if not errorlevel 1 (
    echo ⚠️  Flask secret key ayarlanmamış!
    echo 🔑 Güvenlik için .env dosyasında FLASK_SECRET_KEY değerini ayarlayın.
    echo 💡 Örnek: FLASK_SECRET_KEY=your-super-secret-key-here
    echo.
)

echo ✅ Yapılandırma kontrolleri tamamlandı.
echo.
echo 🌐 Web UI başlatılıyor...
echo 🔗 Erişim URL'leri:
echo    • http://localhost:5000
echo    • http://127.0.0.1:5000
echo.
echo 📊 Loglar aşağıda görünecek:
echo ============================
echo.

REM Port kontrolü
netstat -ano | findstr :5000 >nul
if not errorlevel 1 (
    echo ⚠️  Port 5000 zaten kullanımda!
    echo 🔧 Başka bir uygulama bu portu kullanıyor olabilir.
    echo.
    set /p continue="Devam etmek ister misiniz? (y/n): "
    if /i not "!continue!"=="y" (
        exit /b 1
    )
)

python start_web_ui.py

echo.
echo 🛑 Web UI durduruldu.
echo.
pause