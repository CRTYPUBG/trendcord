@echo off
chcp 65001 >nul
title Trendyol Bot - Unified Web App Deployment

echo ========================================
echo 🚀 UNIFIED WEB APP DEPLOYMENT
echo ========================================
echo.

echo 📋 Bu script şunları yapacak:
echo 1. Unified Web App dosyalarını GitHub'a yükleyecek
echo 2. Uygulamayı başlatacak
echo 3. Cloudflare tunnel kuracak
echo.

set /p confirm="Devam etmek istiyor musunuz? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo İşlem iptal edildi.
    pause
    exit /b
)

echo.
echo 📤 GitHub'a yükleniyor...
powershell -ExecutionPolicy Bypass -File "update_server.ps1" -PushChanges

if errorlevel 1 (
    echo ❌ GitHub yükleme başarısız!
    pause
    exit /b 1
)

echo.
echo 🚀 Unified Web App başlatılıyor...
powershell -ExecutionPolicy Bypass -File "update_server.ps1" -UnifiedApp -NoRestart

echo.
echo ✅ Deployment tamamlandı!
echo.
echo 🔗 Erişim bilgileri:
echo 📱 Yerel: http://localhost:5000
echo 🌐 Public: Cloudflared penceresindeki URL'yi kontrol edin
echo.
echo 🚪 Giriş seçenekleri:
echo 👨‍💼 Admin: /login?type=admin
echo 👤 User: /login?type=user
echo.

pause