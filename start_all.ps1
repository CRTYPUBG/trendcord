# TrendCord Tüm Servisleri Başlatma Scripti
# Web UI, Cloudflare Tunnel ve Discord Bot'u başlatır

param(
    [switch]$WebOnly,
    [switch]$BotOnly,
    [switch]$NoTunnel
)

# Renk fonksiyonları
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Host ""
Write-Host "🚀 TrendCord Tüm Servisler Başlatılıyor" -ForegroundColor Magenta
Write-Host "=======================================" -ForegroundColor Magenta
Write-Host ""

$currentDir = Get-Location
Write-Info "Çalışma dizini: $currentDir"

# .env dosyası kontrolü
if (-not (Test-Path ".env")) {
    Write-Error ".env dosyası bulunamadı! Lütfen .env.example'ı kopyalayın ve düzenleyin."
    exit 1
}

# Virtual environment kontrolü
if (-not (Test-Path "venv/Scripts/Activate.ps1")) {
    Write-Error "Virtual environment bulunamadı! Lütfen install.bat scriptini çalıştırın."
    exit 1
}

# Mevcut servisleri kontrol et
$webRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
$tunnelRunning = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
$botRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

if ($webRunning -or $tunnelRunning -or $botRunning) {
    Write-Warning "Bazı servisler zaten çalışıyor:"
    if ($webRunning) { Write-Info "- Web UI çalışıyor (PID: $($webRunning.Id))" }
    if ($tunnelRunning) { Write-Info "- Cloudflare Tunnel çalışıyor (PID: $($tunnelRunning.Id))" }
    if ($botRunning) { Write-Info "- Discord Bot çalışıyor (PID: $($botRunning.Id))" }
    
    $restart = Read-Host "Servisleri yeniden başlatmak ister misiniz? (y/N)"
    if ($restart -eq "y" -or $restart -eq "Y") {
        Write-Info "Mevcut servisler durduruluyor..."
        if ($webRunning) { $webRunning | Stop-Process -Force }
        if ($tunnelRunning) { $tunnelRunning | Stop-Process -Force }
        if ($botRunning) { $botRunning | Stop-Process -Force }
        Start-Sleep -Seconds 3
    } else {
        Write-Info "Mevcut servisler korunuyor"
        exit 0
    }
}

# Web UI başlat
if (-not $BotOnly) {
    Write-Info "Web UI başlatılıyor..."
    try {
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python start_web_ui.py --port 5000 --host 127.0.0.1" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        
        # Web UI'nin başladığını kontrol et
        $webCheck = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
        if ($webCheck) {
            Write-Success "Web UI başlatıldı (PID: $($webCheck.Id))"
        } else {
            Write-Warning "Web UI başlatılamadı"
        }
    }
    catch {
        Write-Error "Web UI başlatılırken hata: $($_.Exception.Message)"
    }
}

# Cloudflare Tunnel başlat
if (-not $NoTunnel -and -not $BotOnly -and -not $WebOnly) {
    if (Test-Path "cloudflared.exe") {
        Write-Info "Cloudflare Tunnel başlatılıyor..."
        try {
            Start-Process -FilePath ".\cloudflared.exe" -ArgumentList "tunnel", "--url", "http://localhost:5000" -WindowStyle Minimized
            Start-Sleep -Seconds 5
            
            # Tunnel'ın başladığını kontrol et
            $tunnelCheck = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
            if ($tunnelCheck) {
                Write-Success "Cloudflare Tunnel başlatıldı (PID: $($tunnelCheck.Id))"
                Write-Info "Tunnel URL'sini görmek için cloudflared loglarını kontrol edin"
            } else {
                Write-Warning "Cloudflare Tunnel başlatılamadı"
            }
        }
        catch {
            Write-Error "Cloudflare Tunnel başlatılırken hata: $($_.Exception.Message)"
        }
    } else {
        Write-Warning "cloudflared.exe bulunamadı! Tunnel başlatılamadı."
    }
}

# Discord Bot başlat
if (-not $WebOnly) {
    $startBot = $BotOnly
    if (-not $BotOnly) {
        $startBot = (Read-Host "Discord Bot'u da başlatmak ister misiniz? (y/N)") -eq "y"
    }
    
    if ($startBot) {
        Write-Info "Discord Bot başlatılıyor..."
        try {
            Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python main.py" -WindowStyle Minimized
            Start-Sleep -Seconds 3
            
            # Bot'un başladığını kontrol et
            $botCheck = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
            if ($botCheck) {
                Write-Success "Discord Bot başlatıldı (PID: $($botCheck.Id))"
            } else {
                Write-Warning "Discord Bot başlatılamadı"
            }
        }
        catch {
            Write-Error "Discord Bot başlatılırken hata: $($_.Exception.Message)"
        }
    }
}

# Final durum kontrolü
Write-Host ""
Write-Host "📊 Final Servis Durumu:" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

Start-Sleep -Seconds 2

$webFinal = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
$tunnelFinal = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
$botFinal = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

if ($webFinal) {
    Write-Success "Web UI: Çalışıyor (PID: $($webFinal.Id))"
} else {
    Write-Warning "Web UI: Durduruldu"
}

if ($tunnelFinal) {
    Write-Success "Cloudflare Tunnel: Çalışıyor (PID: $($tunnelFinal.Id))"
} else {
    Write-Warning "Cloudflare Tunnel: Durduruldu"
}

if ($botFinal) {
    Write-Success "Discord Bot: Çalışıyor (PID: $($botFinal.Id))"
} else {
    Write-Info "Discord Bot: Durduruldu"
}

# Erişim bilgileri
Write-Host ""
Write-Host "🌐 Erişim Bilgileri:" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "Yerel Web UI: http://localhost:5000" -ForegroundColor Cyan

if ($tunnelFinal) {
    Write-Host "Cloudflare Tunnel: Aktif (URL için tunnel loglarını kontrol edin)" -ForegroundColor Yellow
}

# Port kontrolü
$portCheck = netstat -an | Select-String ":5000.*LISTENING"
if ($portCheck) {
    Write-Success "Port 5000: Dinleniyor"
} else {
    Write-Warning "Port 5000: Dinlenmiyor"
}

Write-Host ""
Write-Success "Tüm işlemler tamamlandı!"
Write-Host ""

# Kullanım örnekleri
Write-Host "💡 Kullanım Örnekleri:" -ForegroundColor Yellow
Write-Host "- Sadece Web UI: .\start_all.ps1 -WebOnly" -ForegroundColor Gray
Write-Host "- Sadece Bot: .\start_all.ps1 -BotOnly" -ForegroundColor Gray
Write-Host "- Tunnel olmadan: .\start_all.ps1 -NoTunnel" -ForegroundColor Gray