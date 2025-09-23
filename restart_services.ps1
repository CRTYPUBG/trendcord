# TrendCord Servis Yeniden Başlatma Scripti
# Sadece servisleri yeniden başlatır, güncelleme yapmaz

param(
    [switch]$WebOnly,
    [switch]$BotOnly,
    [switch]$TunnelOnly
)

# Renk fonksiyonları
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Host ""
Write-Host "🔄 TrendCord Servis Yeniden Başlatma" -ForegroundColor Magenta
Write-Host "====================================" -ForegroundColor Magenta
Write-Host ""

$currentDir = Get-Location
Write-Info "Çalışma dizini: $currentDir"

# Mevcut servisleri durdur
Write-Info "Mevcut servisler durduruluyor..."

if (-not $BotOnly -and -not $TunnelOnly) {
    # Web UI durdur
    Write-Info "Web UI durduruluyor..."
    $webProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
    if ($webProcesses) {
        $webProcesses | Stop-Process -Force
        Write-Success "Web UI durduruldu"
    } else {
        Write-Info "Web UI zaten durdurulmuş"
    }
}

if (-not $WebOnly -and -not $TunnelOnly) {
    # Discord Bot durdur
    Write-Info "Discord Bot durduruluyor..."
    $botProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    if ($botProcesses) {
        $botProcesses | Stop-Process -Force
        Write-Success "Discord Bot durduruldu"
    } else {
        Write-Info "Discord Bot zaten durdurulmuş"
    }
}

if (-not $WebOnly -and -not $BotOnly) {
    # Cloudflare Tunnel durdur
    Write-Info "Cloudflare Tunnel durduruluyor..."
    $tunnelProcesses = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
    if ($tunnelProcesses) {
        $tunnelProcesses | Stop-Process -Force
        Write-Success "Cloudflare Tunnel durduruldu"
    } else {
        Write-Info "Cloudflare Tunnel zaten durdurulmuş"
    }
}

Start-Sleep -Seconds 3

# Servisleri başlat
Write-Info "Servisler başlatılıyor..."

if (-not $BotOnly -and -not $TunnelOnly) {
    # Web UI başlat
    Write-Info "Web UI başlatılıyor..."
    if (Test-Path "venv/Scripts/Activate.ps1") {
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python start_web_ui.py --port 5000 --host 127.0.0.1" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        Write-Success "Web UI başlatıldı"
    } else {
        Write-Error "Virtual environment bulunamadı!"
    }
}

if (-not $WebOnly -and -not $BotOnly) {
    # Cloudflare Tunnel başlat
    if (Test-Path "cloudflared.exe") {
        Write-Info "Cloudflare Tunnel başlatılıyor..."
        Start-Process -FilePath ".\cloudflared.exe" -ArgumentList "tunnel", "--url", "http://localhost:5000" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        Write-Success "Cloudflare Tunnel başlatıldı"
    } else {
        Write-Warning "cloudflared.exe bulunamadı!"
    }
}

if (-not $WebOnly -and -not $TunnelOnly) {
    # Discord Bot başlat
    Write-Info "Discord Bot başlatılıyor..."
    if (Test-Path "venv/Scripts/Activate.ps1") {
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python main.py" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        Write-Success "Discord Bot başlatıldı"
    } else {
        Write-Error "Virtual environment bulunamadı!"
    }
}

# Durum kontrolü
Write-Info "Servis durumu kontrol ediliyor..."
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "📊 Servis Durumu:" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan

$webRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
$tunnelRunning = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
$botRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

if ($webRunning) {
    Write-Success "Web UI: Çalışıyor (PID: $($webRunning.Id))"
} else {
    Write-Warning "Web UI: Durduruldu"
}

if ($tunnelRunning) {
    Write-Success "Cloudflare Tunnel: Çalışıyor (PID: $($tunnelRunning.Id))"
} else {
    Write-Warning "Cloudflare Tunnel: Durduruldu"
}

if ($botRunning) {
    Write-Success "Discord Bot: Çalışıyor (PID: $($botRunning.Id))"
} else {
    Write-Warning "Discord Bot: Durduruldu"
}

Write-Host ""
Write-Host "🌐 Erişim URL'leri:" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host "Yerel: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Cloudflare: Tunnel loglarını kontrol edin" -ForegroundColor Yellow

Write-Host ""
Write-Success "Servis yeniden başlatma tamamlandı!"
Write-Host ""