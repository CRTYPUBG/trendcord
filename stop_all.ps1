# TrendCord Tüm Servisleri Durdurma Scripti
# Web UI, Cloudflare Tunnel ve Discord Bot'u durdurur

param(
    [switch]$WebOnly,
    [switch]$BotOnly,
    [switch]$TunnelOnly,
    [switch]$Force
)

# Renk fonksiyonları
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Host ""
Write-Host "🛑 TrendCord Servisleri Durduruluyor" -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Red
Write-Host ""

# Mevcut servisleri kontrol et
$webRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
$tunnelRunning = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
$botRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

Write-Host "📊 Mevcut Servis Durumu:" -ForegroundColor Cyan
if ($webRunning) { Write-Info "Web UI: Çalışıyor (PID: $($webRunning.Id))" }
if ($tunnelRunning) { Write-Info "Cloudflare Tunnel: Çalışıyor (PID: $($tunnelRunning.Id))" }
if ($botRunning) { Write-Info "Discord Bot: Çalışıyor (PID: $($botRunning.Id))" }

if (-not $webRunning -and -not $tunnelRunning -and -not $botRunning) {
    Write-Success "Hiçbir servis çalışmıyor!"
    exit 0
}

# Onay al (Force parametresi yoksa)
if (-not $Force) {
    $confirm = Read-Host "Servisleri durdurmak istediğinizden emin misiniz? (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Info "İşlem iptal edildi"
        exit 0
    }
}

Write-Host ""
Write-Info "Servisler durduruluyor..."

# Web UI durdur
if ((-not $BotOnly -and -not $TunnelOnly) -and $webRunning) {
    Write-Info "Web UI durduruluyor..."
    try {
        $webRunning | Stop-Process -Force
        Write-Success "Web UI durduruldu"
    }
    catch {
        Write-Error "Web UI durdurulurken hata: $($_.Exception.Message)"
    }
}

# Cloudflare Tunnel durdur
if ((-not $WebOnly -and -not $BotOnly) -and $tunnelRunning) {
    Write-Info "Cloudflare Tunnel durduruluyor..."
    try {
        $tunnelRunning | Stop-Process -Force
        Write-Success "Cloudflare Tunnel durduruldu"
    }
    catch {
        Write-Error "Cloudflare Tunnel durdurulurken hata: $($_.Exception.Message)"
    }
}

# Discord Bot durdur
if ((-not $WebOnly -and -not $TunnelOnly) -and $botRunning) {
    Write-Info "Discord Bot durduruluyor..."
    try {
        $botRunning | Stop-Process -Force
        Write-Success "Discord Bot durduruldu"
    }
    catch {
        Write-Error "Discord Bot durdurulurken hata: $($_.Exception.Message)"
    }
}

# Durum kontrolü
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "📊 Final Durum:" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

$webFinal = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
$tunnelFinal = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
$botFinal = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

if ($webFinal) {
    Write-Warning "Web UI: Hala çalışıyor (PID: $($webFinal.Id))"
} else {
    Write-Success "Web UI: Durduruldu"
}

if ($tunnelFinal) {
    Write-Warning "Cloudflare Tunnel: Hala çalışıyor (PID: $($tunnelFinal.Id))"
} else {
    Write-Success "Cloudflare Tunnel: Durduruldu"
}

if ($botFinal) {
    Write-Warning "Discord Bot: Hala çalışıyor (PID: $($botFinal.Id))"
} else {
    Write-Success "Discord Bot: Durduruldu"
}

# Port kontrolü
$portCheck = netstat -an | Select-String ":5000.*LISTENING"
if ($portCheck) {
    Write-Warning "Port 5000 hala dinleniyor"
} else {
    Write-Success "Port 5000 serbest"
}

Write-Host ""
Write-Success "Durdurma işlemi tamamlandı!"
Write-Host ""

# Kullanım örnekleri
Write-Host "💡 Kullanım Örnekleri:" -ForegroundColor Yellow
Write-Host "- Sadece Web UI durdur: .\stop_all.ps1 -WebOnly" -ForegroundColor Gray
Write-Host "- Sadece Bot durdur: .\stop_all.ps1 -BotOnly" -ForegroundColor Gray
Write-Host "- Onaysız durdur: .\stop_all.ps1 -Force" -ForegroundColor Gray