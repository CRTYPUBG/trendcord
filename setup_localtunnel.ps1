# LocalTunnel Multi-Port Setup

Write-Host "🚀 LocalTunnel Multi-Port Setup" -ForegroundColor Magenta
Write-Host "===============================" -ForegroundColor Magenta

# Node.js kontrolü
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js mevcut: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js bulunamadı!" -ForegroundColor Red
    Write-Host "Node.js indirin: https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

# LocalTunnel kurulumu
Write-Host "📦 LocalTunnel kuruluyor..." -ForegroundColor Cyan
try {
    npm install -g localtunnel
    Write-Host "✅ LocalTunnel kuruldu" -ForegroundColor Green
} catch {
    Write-Host "❌ LocalTunnel kurulamadı" -ForegroundColor Red
    exit 1
}

# Multi-tunnel başlatma scripti oluştur
$startScript = @'
@echo off
title LocalTunnel Multi-Port

echo Starting LocalTunnel for multiple ports...

REM Ana Panel (Port 5000)
start "Main Panel Tunnel" cmd /k "lt --port 5000 --subdomain trendyol-main"

REM Kullanici Paneli (Port 8080)  
start "User Panel Tunnel" cmd /k "lt --port 8080 --subdomain trendyol-user"

echo.
echo Tunnel URLs:
echo Main Panel: https://trendyol-main.loca.lt
echo User Panel: https://trendyol-user.loca.lt
echo.
echo Press any key to stop all tunnels...
pause

REM Tunnellari durdur
taskkill /f /im node.exe
'@

$startScript | Out-File -FilePath "start_localtunnel.bat" -Encoding ASCII

Write-Host "LocalTunnel kurulumu tamamlandi!" -ForegroundColor Green
Write-Host ""
Write-Host "Kullanim:" -ForegroundColor Yellow
Write-Host "start_localtunnel.bat dosyasini calistirin" -ForegroundColor Gray
Write-Host ""
Write-Host "Tunnel URLleri:" -ForegroundColor Green
Write-Host "Ana Panel: https://trendyol-main.loca.lt" -ForegroundColor Cyan
Write-Host "Kullanici Paneli: https://trendyol-user.loca.lt" -ForegroundColor Cyan