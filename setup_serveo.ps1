# Serveo SSH Tunnel Setup

Write-Host "🚀 Serveo SSH Tunnel Setup" -ForegroundColor Magenta
Write-Host "==========================" -ForegroundColor Magenta

# SSH kontrolü
try {
    ssh -V
    Write-Host "✅ SSH mevcut" -ForegroundColor Green
} catch {
    Write-Host "❌ SSH bulunamadı!" -ForegroundColor Red
    Write-Host "OpenSSH'ı Windows Features'dan etkinleştirin" -ForegroundColor Yellow
    exit 1
}

# Serveo tunnel başlatma scripti
$serveoScript = @"
@echo off
title Serveo Multi-Port Tunnels

echo Starting Serveo SSH tunnels...

REM Ana Panel (Port 5000)
start "Main Panel Tunnel" cmd /k "ssh -R trendyol-main:80:localhost:5000 serveo.net"

REM Kullanıcı Paneli (Port 8080)
start "User Panel Tunnel" cmd /k "ssh -R trendyol-user:80:localhost:8080 serveo.net"

echo.
echo Tunnel URLs:
echo Main Panel: https://trendyol-main.serveo.net
echo User Panel: https://trendyol-user.serveo.net
echo.
echo Press any key to stop all tunnels...
pause

REM SSH tunnel'larını durdur
taskkill /f /im ssh.exe
"@

$serveoScript | Out-File -FilePath "start_serveo.bat" -Encoding ASCII

Write-Host "✅ Serveo kurulumu tamamlandı!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Kullanım:" -ForegroundColor Yellow
Write-Host "start_serveo.bat dosyasını çalıştırın" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 Tunnel URL'leri:" -ForegroundColor Green
Write-Host "Ana Panel: https://trendyol-main.serveo.net" -ForegroundColor Cyan
Write-Host "Kullanıcı Paneli: https://trendyol-user.serveo.net" -ForegroundColor Cyan