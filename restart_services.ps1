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
    # Ana Web UI durdur
    Write-Info "Ana Web UI durduruluyor..."
    $webProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
    if ($webProcesses) {
        $webProcesses | Stop-Process -Force
        Write-Success "Ana Web UI durduruldu"
    } else {
        Write-Info "Ana Web UI zaten durdurulmuş"
    }
    
    # Kullanıcı Paneli durdur
    Write-Info "Kullanıcı Paneli durduruluyor..."
    $userPanelProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_user_panel.py*" }
    if ($userPanelProcesses) {
        $userPanelProcesses | Stop-Process -Force
        Write-Success "Kullanıcı Paneli durduruldu"
    } else {
        Write-Info "Kullanıcı Paneli zaten durdurulmuş"
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
    # Ana Web UI başlat
    Write-Info "Ana Web UI başlatılıyor (Port 5000)..."
    if (Test-Path "venv/Scripts/Activate.ps1") {
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python start_web_ui.py --port 5000 --host 127.0.0.1" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        Write-Success "Ana Web UI başlatıldı"
    } else {
        Write-Error "Virtual environment bulunamadı!"
    }
    
    # Kullanıcı Paneli başlat
    Write-Info "Kullanıcı Paneli başlatılıyor (Port 3000)..."
    if (Test-Path "venv/Scripts/Activate.ps1") {
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python start_user_panel.py" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        Write-Success "Kullanıcı Paneli başlatıldı"
    } else {
        Write-Error "Virtual environment bulunamadı!"
    }
}

if (-not $WebOnly -and -not $BotOnly) {
    # Cloudflare Tunnels başlat (Her panel için ayrı)
    $cloudflaredPath = ""
    if (Test-Path "cloudflared.exe") {
        $cloudflaredPath = ".\cloudflared.exe"
    } elseif (Get-Command "cloudflared" -ErrorAction SilentlyContinue) {
        $cloudflaredPath = "cloudflared"
    }
    
    if ($cloudflaredPath) {
        # Ana panel tunnel (Port 5000)
        Write-Info "Ana Panel Cloudflare Tunnel başlatılıyor..."
        Start-Process -FilePath $cloudflaredPath -ArgumentList "tunnel", "--url", "http://localhost:5000" -WindowStyle Minimized
        Start-Sleep -Seconds 5
        Write-Success "Ana Panel Tunnel başlatıldı"
        
        # Kullanıcı paneli tunnel (Port 3000)
        Write-Info "Kullanıcı Paneli Cloudflare Tunnel başlatılıyor..."
        Start-Process -FilePath $cloudflaredPath -ArgumentList "tunnel", "--url", "http://localhost:3000" -WindowStyle Minimized
        Start-Sleep -Seconds 5
        Write-Success "Kullanıcı Paneli Tunnel başlatıldı"
    } else {
        Write-Warning "cloudflared bulunamadı!"
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
$userPanelRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_user_panel.py*" }
$tunnelRunning = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
$botRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

if ($webRunning) {
    Write-Success "Ana Web UI: Çalışıyor (PID: $($webRunning.Id))"
} else {
    Write-Warning "Ana Web UI: Durduruldu"
}

if ($userPanelRunning) {
    Write-Success "Kullanıcı Paneli: Çalışıyor (PID: $($userPanelRunning.Id))"
} else {
    Write-Warning "Kullanıcı Paneli: Durduruldu"
}

if ($tunnelRunning) {
    $tunnelCount = ($tunnelRunning | Measure-Object).Count
    Write-Success "Cloudflare Tunnel: $tunnelCount Çalışıyor"
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
Write-Host "Ana Panel (Yerel): http://localhost:5000" -ForegroundColor Cyan
Write-Host "Kullanıcı Paneli (Yerel): http://localhost:3000" -ForegroundColor Cyan

if ($tunnelRunning) {
    $tunnelCount = ($tunnelRunning | Measure-Object).Count
    Write-Host "Cloudflare Tunnels: $tunnelCount Aktif" -ForegroundColor Yellow
    Write-Host "Ana Panel Tunnel: İlk cloudflared penceresini kontrol edin" -ForegroundColor Yellow
    Write-Host "Kullanıcı Panel Tunnel: İkinci cloudflared penceresini kontrol edin" -ForegroundColor Yellow
}

Write-Host ""
Write-Success "Servis yeniden başlatma tamamlandı!"
Write-Host ""