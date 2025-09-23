@echo off
title TrendCord Windows Kurulum
color 0A

echo.
echo  ████████╗██████╗ ███████╗███╗   ██╗██████╗  ██████╗ ██████╗ ██████╗ 
echo  ╚══██╔══╝██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
echo     ██║   ██████╔╝█████╗  ██╔██╗ ██║██║  ██║██║     ██║   ██║██████╔╝
echo     ██║   ██╔══██╗██╔══╝  ██║╚██╗██║██║  ██║██║     ██║   ██║██╔══██╗
echo     ██║   ██║  ██║███████╗██║ ╚████║██████╔╝╚██████╗╚██████╔╝██║  ██║
echo     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
echo.
echo                    🚀 Windows Kurulum Scripti v2.0
echo                    ================================
echo.

REM Yönetici kontrolü
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Yönetici yetkileri tespit edildi.
) else (
    echo ⚠️  Bu script yönetici yetkileri gerektirebilir.
    echo    Chocolatey kurulumu için PowerShell'i yönetici olarak çalıştırın.
)

echo.
echo 📋 Kurulum Adımları:
echo    1. Chocolatey kurulumu
echo    2. Gerekli araçları kurma
echo    3. Python ortamı hazırlama
echo    4. TrendCord kurulumu
echo.

pause

REM Chocolatey kontrolü
choco --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Chocolatey bulunamadı!
    echo.
    echo 📥 Chocolatey kurulumu için şu komutu PowerShell'de (Yönetici olarak) çalıştırın:
    echo.
    echo Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    echo.
    echo 🔄 Chocolatey kurulduktan sonra bu scripti tekrar çalıştırın.
    pause
    exit /b 1
) else (
    echo ✅ Chocolatey bulundu.
)

REM Curl kontrolü ve kurulumu
curl --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📥 Curl kuruluyor...
    choco install curl -y
    if errorlevel 1 (
        echo ❌ Curl kurulumu başarısız!
        pause
        exit /b 1
    )
    echo ✅ Curl kuruldu.
) else (
    echo ✅ Curl zaten kurulu.
)

REM Git kontrolü ve kurulumu
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📥 Git kuruluyor...
    choco install git -y
    if errorlevel 1 (
        echo ❌ Git kurulumu başarısız!
        pause
        exit /b 1
    )
    echo ✅ Git kuruldu.
    echo 🔄 PATH yenileniyor...
    call refreshenv
) else (
    echo ✅ Git zaten kurulu.
)

REM Python kontrolü ve kurulumu
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📥 Python kuruluyor...
    choco install python -y
    if errorlevel 1 (
        echo ❌ Python kurulumu başarısız!
        pause
        exit /b 1
    )
    echo ✅ Python kuruldu.
    echo 🔄 PATH yenileniyor...
    call refreshenv
) else (
    echo ✅ Python zaten kurulu.
)

echo.
echo 🚀 TrendCord Kurulumu Başlıyor...
echo ================================

REM Virtual environment oluştur
echo 📦 Virtual environment oluşturuluyor...
python -m venv venv
if errorlevel 1 (
    echo ❌ Virtual environment oluşturulamadı!
    pause
    exit /b 1
)

REM Virtual environment aktive et
echo 🔧 Virtual environment aktive ediliyor...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Virtual environment aktive edilemedi!
    pause
    exit /b 1
)

REM Pip güncelle
echo 📚 Pip güncelleniyor...
python -m pip install --upgrade pip

REM Gereksinimler kur
echo 📚 Gereksinimler kuruluyor...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Gereksinimler kurulunamadı!
    pause
    exit /b 1
)

REM .env dosyası oluştur
if not exist .env (
    echo 📝 .env dosyası oluşturuluyor...
    copy .env.example .env >nul
    echo ✅ .env dosyası oluşturuldu.
) else (
    echo ✅ .env dosyası zaten mevcut.
)

REM Veri klasörleri oluştur
if not exist data mkdir data
if not exist logs mkdir logs
echo ✅ Veri klasörleri oluşturuldu.

REM Batch scriptleri oluştur
echo 📄 Yönetim scriptleri oluşturuluyor...

REM start_bot.bat
echo @echo off > start_bot.bat
echo title TrendCord Discord Bot >> start_bot.bat
echo color 0B >> start_bot.bat
echo echo 🤖 TrendCord Discord Bot Başlatılıyor... >> start_bot.bat
echo cd /d "%%~dp0" >> start_bot.bat
echo call venv\Scripts\activate.bat >> start_bot.bat
echo python main.py >> start_bot.bat
echo pause >> start_bot.bat

REM start_web.bat
echo @echo off > start_web.bat
echo title TrendCord Web UI >> start_web.bat
echo color 0C >> start_web.bat
echo echo 🌐 TrendCord Web UI Başlatılıyor... >> start_web.bat
echo cd /d "%%~dp0" >> start_web.bat
echo call venv\Scripts\activate.bat >> start_web.bat
echo python start_web_ui.py >> start_web.bat
echo pause >> start_web.bat

REM update.bat
echo @echo off > update.bat
echo title TrendCord Güncelleme >> update.bat
echo color 0E >> update.bat
echo echo 🔄 TrendCord Güncelleniyor... >> update.bat
echo cd /d "%%~dp0" >> update.bat
echo git pull origin main >> update.bat
echo call venv\Scripts\activate.bat >> update.bat
echo pip install -r requirements.txt >> update.bat
echo echo ✅ Güncelleme tamamlandı! >> update.bat
echo pause >> update.bat

REM test.bat
echo @echo off > test.bat
echo title TrendCord Test >> test.bat
echo color 0D >> test.bat
echo echo 🧪 TrendCord Test Ediliyor... >> test.bat
echo cd /d "%%~dp0" >> test.bat
echo call venv\Scripts\activate.bat >> test.bat
echo python test_analytics_system.py >> test.bat
echo pause >> test.bat

echo ✅ Yönetim scriptleri oluşturuldu.

echo.
echo 🎉 TrendCord Kurulumu Tamamlandı!
echo ================================
echo.
echo 📋 Sonraki Adımlar:
echo    1. .env dosyasını düzenleyin (Discord token ekleyin)
echo    2. start_bot.bat ile Discord bot'unu başlatın
echo    3. start_web.bat ile Web UI'yi başlatın
echo.
echo 📄 Oluşturulan Dosyalar:
echo    • start_bot.bat    - Discord bot başlatıcı
echo    • start_web.bat    - Web UI başlatıcı
echo    • update.bat       - Güncelleme scripti
echo    • test.bat         - Test scripti
echo.
echo 🔗 Erişim URL'leri:
echo    • Web UI: http://localhost:5000
echo    • Dashboard: http://127.0.0.1:5000
echo.
echo ⚠️  ÖNEMLI NOTLAR:
echo    • .env dosyasında Discord token'ınızı ayarlayın
echo    • Bot'u Discord sunucunuza davet etmeyi unutmayın
echo    • İlk çalıştırmada Windows Defender uyarısı çıkabilir
echo.

REM .env dosyasını aç
set /p open_env="📝 .env dosyasını şimdi düzenlemek ister misiniz? (y/n): "
if /i "%open_env%"=="y" (
    notepad .env
)

echo.
echo 🚀 TrendCord kullanıma hazır!
echo.
pause