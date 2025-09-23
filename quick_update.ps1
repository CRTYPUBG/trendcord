# TrendCord Hızlı Güncelleme Scripti
# Minimum işlemle hızlı güncelleme yapar

Write-Host "🚀 TrendCord Hızlı Güncelleme" -ForegroundColor Magenta
Write-Host "=============================" -ForegroundColor Magenta

# Git pull
Write-Host "📥 Değişiklikler çekiliyor..." -ForegroundColor Cyan
git pull origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Güncelleme başarılı!" -ForegroundColor Green
} else {
    Write-Host "❌ Güncelleme başarısız!" -ForegroundColor Red
    exit 1
}

# Python paketleri güncelle
if (Test-Path "venv/Scripts/Activate.ps1") {
    Write-Host "📦 Python paketleri güncelleniyor..." -ForegroundColor Cyan
    & "venv/Scripts/Activate.ps1"
    pip install -r requirements.txt --upgrade --quiet
    Write-Host "✅ Paketler güncellendi!" -ForegroundColor Green
}

# Servisleri yeniden başlat
Write-Host "🔄 Servisler yeniden başlatılıyor..." -ForegroundColor Cyan

# Web UI'yi yeniden başlat
$webProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
if ($webProcesses) {
    $webProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

$currentDir = Get-Location
Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python start_web_ui.py --port 5000 --host 127.0.0.1" -WindowStyle Minimized

Write-Host "✅ Hızlı güncelleme tamamlandı!" -ForegroundColor Green
Write-Host "🌐 Web UI: http://localhost:5000" -ForegroundColor Cyan