# Bore Tunnel Setup

Write-Host "🚀 Bore Tunnel Setup" -ForegroundColor Magenta
Write-Host "====================" -ForegroundColor Magenta

# Bore indirme
$boreUrl = "https://github.com/ekzhang/bore/releases/latest/download/bore-v0.5.0-x86_64-pc-windows-msvc.exe"
$boreExe = "bore.exe"

if (-not (Test-Path $boreExe)) {
    Write-Host "📥 Bore indiriliyor..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $boreUrl -OutFile $boreExe
        Write-Host "✅ Bore indirildi" -ForegroundColor Green
    } catch {
        Write-Host "❌ Bore indirilemedi" -ForegroundColor Red
        exit 1
    }
}

# Bore multi-tunnel scripti
$boreScript = @"
@echo off
title Bore Multi-Port Tunnels

echo Starting Bore tunnels...

REM Ana Panel (Port 5000)
start "Main Panel Tunnel" cmd /k "bore.exe local 5000 --to bore.pub"

REM Kullanıcı Paneli (Port 8080)
start "User Panel Tunnel" cmd /k "bore.exe local 8080 --to bore.pub"

echo.
echo Tunnel URLs will be displayed in the opened windows
echo.
pause
"@

$boreScript | Out-File -FilePath "start_bore.bat" -Encoding ASCII

Write-Host "✅ Bore kurulumu tamamlandı!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Kullanım:" -ForegroundColor Yellow
Write-Host "start_bore.bat dosyasını çalıştırın" -ForegroundColor Gray