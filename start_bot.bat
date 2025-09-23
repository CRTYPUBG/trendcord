@echo off
title TrendCord Discord Bot
color 0B

echo.
echo  ████████╗██████╗ ███████╗███╗   ██╗██████╗  ██████╗ ██████╗ ██████╗ 
echo  ╚══██╔══╝██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
echo     ██║   ██████╔╝█████╗  ██╔██╗ ██║██║  ██║██║     ██║   ██║██████╔╝
echo     ██║   ██╔══██╗██╔══╝  ██║╚██╗██║██║  ██║██║     ██║   ██║██╔══██╗
echo     ██║   ██║  ██║███████╗██║ ╚████║██████╔╝╚██████╗╚██████╔╝██║  ██║
echo     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
echo.
echo                        🤖 Discord Bot Başlatılıyor...
echo                        ==============================
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

REM Discord token kontrolü
findstr /C:"DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN" .env >nul
if not errorlevel 1 (
    echo ❌ Discord token ayarlanmamış!
    echo 🔑 Lütfen .env dosyasında DISCORD_TOKEN değerini ayarlayın.
    echo.
    set /p open_env="📝 .env dosyasını şimdi düzenlemek ister misiniz? (y/n): "
    if /i "!open_env!"=="y" (
        notepad .env
        echo 🔄 .env dosyasını düzenledikten sonra bu scripti tekrar çalıştırın.
    )
    pause
    exit /b 1
)

echo ✅ Yapılandırma kontrolleri tamamlandı.
echo.
echo 🚀 Discord Bot başlatılıyor...
echo 📊 Loglar aşağıda görünecek:
echo ================================
echo.

python main.py

echo.
echo 🛑 Bot durduruldu.
echo.
pause