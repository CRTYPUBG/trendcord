# Cloudflare Tunnel Setup Script
# Unified Web App için Cloudflare tunnel kurulumu

param(
    [string]$Domain = "",
    [int]$Port = 5000,
    [string]$TunnelName = "trendyol-bot-unified"
)

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "🌐 CLOUDFLARE TUNNEL SETUP - UNIFIED WEB APP" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 60) -ForegroundColor Cyan

# Cloudflared kurulu mu kontrol et
Write-Host "📦 Cloudflared kontrol ediliyor..." -ForegroundColor Blue
$cloudflaredPath = Get-Command cloudflared -ErrorAction SilentlyContinue

if (-not $cloudflaredPath) {
    Write-Host "❌ Cloudflared bulunamadı! Yükleniyor..." -ForegroundColor Red
    
    # Cloudflared'i indir ve yükle
    $downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    $installPath = "$env:ProgramFiles\Cloudflared"
    
    if (-not (Test-Path $installPath)) {
        New-Item -ItemType Directory -Path $installPath -Force | Out-Null
    }
    
    $exePath = "$installPath\cloudflared.exe"
    
    try {
        Write-Host "⬇️  Cloudflared indiriliyor..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath -UseBasicParsing
        
        # PATH'e ekle
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        if ($currentPath -notlike "*$installPath*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$installPath", "Machine")
            $env:PATH += ";$installPath"
        }
        
        Write-Host "✅ Cloudflared başarıyla yüklendi!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Cloudflared yüklenemedi: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✅ Cloudflared zaten yüklü: $($cloudflaredPath.Source)" -ForegroundColor Green
}

# Cloudflare'e giriş yap
Write-Host "`n🔐 Cloudflare hesabına giriş yapılıyor..." -ForegroundColor Blue
Write-Host "Tarayıcıda açılan sayfadan giriş yapın ve yetkilendirin." -ForegroundColor Yellow

try {
    & cloudflared tunnel login
    if ($LASTEXITCODE -ne 0) {
        throw "Cloudflare giriş başarısız"
    }
    Write-Host "✅ Cloudflare girişi başarılı!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Cloudflare girişi başarısız: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Tunnel oluştur
Write-Host "`n🚇 Tunnel oluşturuluyor..." -ForegroundColor Blue
try {
    $existingTunnel = & cloudflared tunnel list --output json 2>$null | ConvertFrom-Json | Where-Object { $_.name -eq $TunnelName }
    
    if ($existingTunnel) {
        Write-Host "⚠️  '$TunnelName' tunnel'i zaten mevcut, kullanılıyor..." -ForegroundColor Yellow
        $tunnelId = $existingTunnel.id
    }
    else {
        & cloudflared tunnel create $TunnelName
        if ($LASTEXITCODE -ne 0) {
            throw "Tunnel oluşturulamadı"
        }
        
        $tunnelInfo = & cloudflared tunnel list --output json | ConvertFrom-Json | Where-Object { $_.name -eq $TunnelName }
        $tunnelId = $tunnelInfo.id
        Write-Host "✅ Tunnel oluşturuldu: $tunnelId" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Tunnel oluşturma hatası: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Domain yapılandırması
if (-not $Domain) {
    Write-Host "`n🌐 Domain yapılandırması..." -ForegroundColor Blue
    Write-Host "Cloudflare'de yönettiğiniz bir domain adı girin (örn: example.com):" -ForegroundColor Yellow
    $Domain = Read-Host "Domain"
    
    if (-not $Domain) {
        Write-Host "❌ Domain gerekli!" -ForegroundColor Red
        exit 1
    }
}

$subdomain = "trendyol-bot"
$fullDomain = "$subdomain.$Domain"

# DNS kaydı oluştur
Write-Host "`n📝 DNS kaydı oluşturuluyor..." -ForegroundColor Blue
try {
    & cloudflared tunnel route dns $TunnelName $fullDomain
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  DNS kaydı zaten mevcut olabilir, devam ediliyor..." -ForegroundColor Yellow
    }
    else {
        Write-Host "✅ DNS kaydı oluşturuldu: $fullDomain" -ForegroundColor Green
    }
}
catch {
    Write-Host "⚠️  DNS kaydı oluşturma uyarısı: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Konfigürasyon dosyası oluştur
Write-Host "`n⚙️  Konfigürasyon dosyası oluşturuluyor..." -ForegroundColor Blue

$configDir = "$env:USERPROFILE\.cloudflared"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$configFile = "$configDir\config.yml"
$configContent = @"
tunnel: $tunnelId
credentials-file: $configDir\$tunnelId.json

ingress:
  - hostname: $fullDomain
    service: http://localhost:$Port
  - service: http_status:404
"@

$configContent | Out-File -FilePath $configFile -Encoding UTF8
Write-Host "✅ Konfigürasyon dosyası oluşturuldu: $configFile" -ForegroundColor Green

# .env dosyasını güncelle
Write-Host "`n📄 .env dosyası güncelleniyor..." -ForegroundColor Blue
$envFile = ".env"

if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    
    # Mevcut değerleri güncelle veya ekle
    $updates = @{
        "WEB_PORT" = $Port
        "WEB_HOST" = "0.0.0.0"
        "CLOUDFLARE_TUNNEL_URL" = "https://$fullDomain"
        "DISCORD_REDIRECT_URI" = "https://$fullDomain/auth/callback"
        "ADMIN_SECRET_KEY" = "admin123"  # Güvenlik için değiştirin!
    }
    
    foreach ($key in $updates.Keys) {
        $value = $updates[$key]
        if ($envContent -match "^$key=") {
            $envContent = $envContent -replace "^$key=.*", "$key=$value"
        }
        else {
            $envContent += "`n$key=$value"
        }
    }
    
    $envContent | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "✅ .env dosyası güncellendi" -ForegroundColor Green
}
else {
    Write-Host "⚠️  .env dosyası bulunamadı, örnek dosya oluşturuluyor..." -ForegroundColor Yellow
    
    $envContent = @"
# Unified Web App Configuration
WEB_PORT=$Port
WEB_HOST=0.0.0.0
CLOUDFLARE_TUNNEL_URL=https://$fullDomain
DISCORD_REDIRECT_URI=https://$fullDomain/auth/callback

# Admin Configuration
ADMIN_SECRET_KEY=admin123

# Discord OAuth (Discord Developer Portal'dan alın)
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret

# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_PATH=data/trendyol_bot.db
"@
    
    $envContent | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "✅ .env dosyası oluşturuldu" -ForegroundColor Green
}

# Başlatma scripti oluştur
Write-Host "`n🚀 Başlatma scripti oluşturuluyor..." -ForegroundColor Blue

$startScript = @"
@echo off
title Trendyol Bot - Unified Web App with Cloudflare Tunnel

echo ================================
echo 🚀 TRENDYOL BOT - UNIFIED WEB APP
echo ================================

echo 📦 Python sanal ortamı aktifleştiriliyor...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  Sanal ortam bulunamadı, sistem Python kullanılıyor...
)

echo 🌐 Cloudflare tunnel başlatılıyor...
start /B cloudflared tunnel run $TunnelName

echo ⏳ Tunnel'in başlaması bekleniyor...
timeout /t 5 /nobreak >nul

echo 🌍 Web uygulaması başlatılıyor...
echo 📱 Yerel erişim: http://localhost:$Port
echo 🌐 Genel erişim: https://$fullDomain
echo.
echo Admin Giriş: https://$fullDomain/login?type=admin
echo User Giriş: https://$fullDomain/login?type=user
echo.

python unified_web_app.py

echo.
echo 🛑 Uygulama durduruldu.
pause
"@

$startScript | Out-File -FilePath "start_unified_app.bat" -Encoding UTF8
Write-Host "✅ Başlatma scripti oluşturuldu: start_unified_app.bat" -ForegroundColor Green

# Durdurma scripti oluştur
$stopScript = @"
@echo off
title Trendyol Bot - Stop Services

echo 🛑 Trendyol Bot servisleri durduruluyor...

echo 📱 Web uygulaması durduruluyor...
taskkill /F /IM python.exe 2>nul

echo 🌐 Cloudflare tunnel durduruluyor...
taskkill /F /IM cloudflared.exe 2>nul

echo ✅ Tüm servisler durduruldu.
pause
"@

$stopScript | Out-File -FilePath "stop_unified_app.bat" -Encoding UTF8
Write-Host "✅ Durdurma scripti oluşturuldu: stop_unified_app.bat" -ForegroundColor Green

# Özet bilgiler
Write-Host "`n" -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host ("=" * 60) -ForegroundColor Green
Write-Host "✅ CLOUDFLARE TUNNEL KURULUMU TAMAMLANDI!" -ForegroundColor Green
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host ("=" * 60) -ForegroundColor Green

Write-Host "`n📋 KURULUM ÖZETİ:" -ForegroundColor Yellow
Write-Host "🌐 Tunnel Adı: $TunnelName" -ForegroundColor White
Write-Host "🌍 Public URL: https://$fullDomain" -ForegroundColor White
Write-Host "📱 Local URL: http://localhost:$Port" -ForegroundColor White
Write-Host "⚙️  Config: $configFile" -ForegroundColor White

Write-Host "`n🔗 ERİŞİM LİNKLERİ:" -ForegroundColor Yellow
Write-Host "👨‍💼 Admin Paneli: https://$fullDomain/login?type=admin" -ForegroundColor Cyan
Write-Host "👤 Kullanıcı Paneli: https://$fullDomain/login?type=user" -ForegroundColor Cyan

Write-Host "`n⚡ HIZLI BAŞLATMA:" -ForegroundColor Yellow
Write-Host "1. start_unified_app.bat dosyasını çalıştırın" -ForegroundColor White
Write-Host "2. Tarayıcıda https://$fullDomain adresine gidin" -ForegroundColor White
Write-Host "3. Admin veya User girişi yapın" -ForegroundColor White

Write-Host "`n⚠️  ÖNEMLİ NOTLAR:" -ForegroundColor Red
Write-Host "• Discord OAuth ayarlarını Discord Developer Portal'dan yapın" -ForegroundColor Yellow
Write-Host "• .env dosyasındaki DISCORD_CLIENT_ID ve DISCORD_CLIENT_SECRET değerlerini güncelleyin" -ForegroundColor Yellow
Write-Host "• ADMIN_SECRET_KEY değerini güvenlik için değiştirin" -ForegroundColor Yellow
Write-Host "• Redirect URI: https://$fullDomain/auth/callback" -ForegroundColor Yellow

Write-Host "`n🚀 Başlatmak için: .\start_unified_app.bat" -ForegroundColor Green
Write-Host "🛑 Durdurmak için: .\stop_unified_app.bat" -ForegroundColor Red

Write-Host "`n" -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host ("=" * 60) -ForegroundColor Green