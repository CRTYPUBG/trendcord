# Ngrok Hizli Kurulum

Write-Host "Ngrok Hizli Kurulum" -ForegroundColor Magenta

# Ngrok indirme
$ngrokUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
$ngrokZip = "ngrok.zip"

if (-not (Test-Path "ngrok.exe")) {
    Write-Host "Ngrok indiriliyor..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $ngrokUrl -OutFile $ngrokZip
        Expand-Archive -Path $ngrokZip -DestinationPath . -Force
        Remove-Item $ngrokZip
        Write-Host "Ngrok indirildi" -ForegroundColor Green
    } catch {
        Write-Host "Ngrok indirilemedi" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Ngrok tunnel baslatiliyor..." -ForegroundColor Cyan

# Ana panel tunnel
Start-Process -FilePath ".\ngrok.exe" -ArgumentList "http", "5000" -WindowStyle Normal

Start-Sleep -Seconds 2

# Kullanici paneli tunnel
Start-Process -FilePath ".\ngrok.exe" -ArgumentList "http", "8080" -WindowStyle Normal

Write-Host "Ngrok tunnels baslatildi!" -ForegroundColor Green
Write-Host "Ngrok dashboard: http://localhost:4040" -ForegroundColor Yellow