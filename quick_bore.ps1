# Bore Tunnel Hızlı Kurulum

Write-Host "🚀 Bore Tunnel Kurulum" -ForegroundColor Magenta

# Bore indirme
$boreUrl = "https://github.com/ekzhang/bore/releases/download/v0.5.0/bore-v0.5.0-x86_64-pc-windows-msvc.exe"

if (-not (Test-Path "bore.exe")) {
    Write-Host "📥 Bore indiriliyor..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $boreUrl -OutFile "bore.exe"
        Write-Host "✅ Bore indirildi" -ForegroundColor Green
    } catch {
        Write-Host "❌ Bore indirilemedi" -ForegroundColor Red
        exit 1
    }
}

Write-Host "🌐 Bore tunnels başlatılıyor..." -ForegroundColor Cyan

# Ana panel tunnel
Start-Process -FilePath ".\bore.exe" -ArgumentList "local", "5000", "--to", "bore.pub" -WindowStyle Normal

Start-Sleep -Seconds 2

# Kullanıcı paneli tunnel
Start-Process -FilePath ".\bore.exe" -ArgumentList "local", "8080", "--to", "bore.pub" -WindowStyle Normal

Write-Host "✅ Bore tunnels başlatıldı!" -ForegroundColor Green
Write-Host "📋 URL'ler açılan pencerelerde görünecek" -ForegroundColor Yellow