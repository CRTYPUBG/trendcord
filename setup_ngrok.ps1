# Ngrok Kurulum ve Multi-Port Setup

Write-Host "🚀 Ngrok Multi-Port Setup" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta

# Ngrok indirme ve kurulum
$ngrokUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
$ngrokZip = "ngrok.zip"
$ngrokExe = "ngrok.exe"

if (-not (Test-Path $ngrokExe)) {
    Write-Host "📥 Ngrok indiriliyor..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $ngrokUrl -OutFile $ngrokZip
        Expand-Archive -Path $ngrokZip -DestinationPath . -Force
        Remove-Item $ngrokZip
        Write-Host "✅ Ngrok indirildi" -ForegroundColor Green
    } catch {
        Write-Host "❌ Ngrok indirilemedi: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Ngrok config dosyası oluştur
$ngrokConfig = @"
version: "2"
authtoken: YOUR_NGROK_AUTH_TOKEN_HERE
tunnels:
  main-panel:
    addr: 5000
    proto: http
    subdomain: trendyol-main
  user-panel:
    addr: 8080
    proto: http
    subdomain: trendyol-user
"@

$ngrokConfig | Out-File -FilePath "ngrok.yml" -Encoding UTF8

Write-Host "📝 Ngrok config oluşturuldu: ngrok.yml" -ForegroundColor Green

Write-Host ""
Write-Host "🔧 Kurulum Adımları:" -ForegroundColor Yellow
Write-Host "1. https://ngrok.com adresine git ve hesap oluştur" -ForegroundColor Gray
Write-Host "2. Auth token'ını al" -ForegroundColor Gray
Write-Host "3. ngrok.yml dosyasında YOUR_NGROK_AUTH_TOKEN_HERE yerine token'ı yaz" -ForegroundColor Gray
Write-Host "4. .\start_ngrok_tunnels.ps1 çalıştır" -ForegroundColor Gray

Write-Host ""
Write-Host "🌐 Tunnel URL'leri:" -ForegroundColor Green
Write-Host "Ana Panel: https://trendyol-main.ngrok.io" -ForegroundColor Cyan
Write-Host "Kullanıcı Paneli: https://trendyol-user.ngrok.io" -ForegroundColor Cyan