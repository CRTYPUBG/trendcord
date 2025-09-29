# Ngrok Multi-Tunnel Başlatma

Write-Host "🚀 Ngrok Multi-Tunnel Başlatılıyor" -ForegroundColor Magenta

# Ngrok'un kurulu olup olmadığını kontrol et
if (-not (Test-Path "ngrok.exe")) {
    Write-Host "❌ Ngrok bulunamadı! Önce setup_ngrok.ps1 çalıştırın" -ForegroundColor Red
    exit 1
}

# Config dosyasını kontrol et
if (-not (Test-Path "ngrok.yml")) {
    Write-Host "❌ ngrok.yml bulunamadı!" -ForegroundColor Red
    exit 1
}

# Auth token kontrolü
$configContent = Get-Content "ngrok.yml" -Raw
if ($configContent -match "YOUR_NGROK_AUTH_TOKEN_HERE") {
    Write-Host "❌ Auth token ayarlanmamış! ngrok.yml dosyasını düzenleyin" -ForegroundColor Red
    Write-Host "1. https://ngrok.com adresine gidin" -ForegroundColor Yellow
    Write-Host "2. Hesap oluşturun/giriş yapın" -ForegroundColor Yellow
    Write-Host "3. Auth token'ınızı alın" -ForegroundColor Yellow
    Write-Host "4. ngrok.yml dosyasında YOUR_NGROK_AUTH_TOKEN_HERE yerine yazın" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Ngrok config hazır" -ForegroundColor Green

# Servislerin çalışıp çalışmadığını kontrol et
$mainPanel = netstat -an | Select-String ":5000.*LISTENING"
$userPanel = netstat -an | Select-String ":8080.*LISTENING"

if (-not $mainPanel) {
    Write-Host "⚠️  Ana panel (Port 5000) çalışmıyor" -ForegroundColor Yellow
}

if (-not $userPanel) {
    Write-Host "⚠️  Kullanıcı paneli (Port 8080) çalışmıyor" -ForegroundColor Yellow
}

# Ngrok tunnel'larını başlat
Write-Host "🌐 Tunnel'lar başlatılıyor..." -ForegroundColor Cyan

try {
    # Tüm tunnel'ları aynı anda başlat
    Start-Process -FilePath ".\ngrok.exe" -ArgumentList "start", "--all", "--config", "ngrok.yml" -WindowStyle Minimized
    
    Start-Sleep -Seconds 5
    
    Write-Host "✅ Ngrok tunnel'ları başlatıldı!" -ForegroundColor Green
    
    # Tunnel durumunu kontrol et
    $ngrokProcess = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
    if ($ngrokProcess) {
        Write-Host "✅ Ngrok process çalışıyor (PID: $($ngrokProcess.Id))" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "🌐 Tunnel URL'leri:" -ForegroundColor Green
    Write-Host "Ana Panel: https://trendyol-main.ngrok.io" -ForegroundColor Cyan
    Write-Host "Kullanıcı Paneli: https://trendyol-user.ngrok.io" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "📊 Ngrok Dashboard: http://localhost:4040" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Ngrok başlatılamadı: $($_.Exception.Message)" -ForegroundColor Red
}