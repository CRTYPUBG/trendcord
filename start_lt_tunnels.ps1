# LocalTunnel Hızlı Başlatma

Write-Host "🚀 LocalTunnel Başlatılıyor..." -ForegroundColor Magenta

# LocalTunnel kontrolü
try {
    lt --help | Out-Null
    Write-Host "✅ LocalTunnel hazır" -ForegroundColor Green
} catch {
    Write-Host "❌ LocalTunnel bulunamadı! Kuruluyor..." -ForegroundColor Red
    npm install -g localtunnel
}

# Port kontrolü
$port5000 = netstat -an | Select-String ":5000.*LISTENING"
$port8080 = netstat -an | Select-String ":8080.*LISTENING"

if (-not $port5000) {
    Write-Host "⚠️  Ana panel (Port 5000) çalışmıyor" -ForegroundColor Yellow
}

if (-not $port8080) {
    Write-Host "⚠️  Kullanıcı paneli (Port 8080) çalışmıyor" -ForegroundColor Yellow
}

# Tunnel'ları başlat
Write-Host "🌐 Tunnel'lar başlatılıyor..." -ForegroundColor Cyan

# Ana panel tunnel
Start-Process -FilePath "cmd" -ArgumentList "/k", "title Main Panel Tunnel && echo Ana Panel Tunnel Baslatiliyor... && lt --port 5000" -WindowStyle Normal

Start-Sleep -Seconds 2

# Kullanıcı paneli tunnel
Start-Process -FilePath "cmd" -ArgumentList "/k", "title User Panel Tunnel && echo Kullanici Panel Tunnel Baslatiliyor... && lt --port 8080" -WindowStyle Normal

Write-Host "✅ Tunnel'lar başlatıldı!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Tunnel URL'lerini görmek için açılan cmd pencerelerini kontrol edin" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔗 Tipik URL formatı:" -ForegroundColor Cyan
Write-Host "https://random-name-123.loca.lt" -ForegroundColor Gray