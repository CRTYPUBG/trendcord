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

# Ana Web UI başlat
if (-not $BotOnly) {
    Write-Info "Ana Web UI başlatılıyor (Port 5000)..."
    try {
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python start_web_ui.py --port 5000 --host 127.0.0.1" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        
        # Ana Web UI'nin başladığını kontrol et
        $webCheck = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
        if ($webCheck) {
            Write-Success "Ana Web UI başlatıldı (PID: $($webCheck.Id))"
        } else {
            Write-Warning "Ana Web UI başlatılamadı"
        }
    }
    catch {
        Write-Error "Ana Web UI başlatılırken hata: $($_.Exception.Message)"
    }
    
    # Kullanıcı Paneli başlat
    Write-Info "Kullanıcı Paneli başlatılıyor (Port 3000)..."
    try {
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python start_user_panel.py" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        
        # Kullanıcı Paneli'nin başladığını kontrol et
        $userPanelCheck = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_user_panel.py*" }
        if ($userPanelCheck) {
            Write-Success "Kullanıcı Paneli başlatıldı (PID: $($userPanelCheck.Id))"
        } else {
            Write-Warning "Kullanıcı Paneli başlatılamadı"
        }
    }
    catch {
        Write-Error "Kullanıcı Paneli başlatılırken hata: $($_.Exception.Message)"
    }
}

# Cloudflare Tunnels başlat (Her panel için ayrı)
if (-not $NoTunnel -and -not $BotOnly -and -not $WebOnly) {
    $cloudflaredPath = ""
    if (Test-Path "cloudflared.exe") {
        $cloudflaredPath = ".\cloudflared.exe"
    } elseif (Get-Command "cloudflared" -ErrorAction SilentlyContinue) {
        $cloudflaredPath = "cloudflared"
    }
    
    if ($cloudflaredPath) {
        try {
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
            
            # Tunnel kontrolü
            $tunnelCheck = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
            if ($tunnelCheck) {
                $tunnelCount = ($tunnelCheck | Measure-Object).Count
                Write-Success "$tunnelCount Cloudflare Tunnel başlatıldı"
                Write-Info "Tunnel URL'lerini görmek için cloudflared pencerelerini kontrol edin"
            } else {
                Write-Warning "Cloudflare Tunnels başlatılamadı"
            }
        }
        catch {
            Write-Error "Cloudflare Tunnels başlatılırken hata: $($_.Exception.Message)"
        }
    } else {
        Write-Warning "cloudflared bulunamadı! Tunnels başlatılamadı."
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
$userPanelFinal = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_user_panel.py*" }
$tunnelFinal = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
$botFinal = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

if ($webFinal) {
    Write-Success "Ana Web UI: Çalışıyor (PID: $($webFinal.Id))"
} else {
    Write-Warning "Ana Web UI: Durduruldu"
}

if ($userPanelFinal) {
    Write-Success "Kullanıcı Paneli: Çalışıyor (PID: $($userPanelFinal.Id))"
} else {
    Write-Warning "Kullanıcı Paneli: Durduruldu"
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
Write-Host "Ana Panel (Yerel): http://localhost:5000" -ForegroundColor Cyan
Write-Host "Kullanıcı Paneli (Yerel): http://localhost:3000" -ForegroundColor Cyan

if ($tunnelFinal) {
    $tunnelCount = ($tunnelFinal | Measure-Object).Count
    Write-Host "Cloudflare Tunnels: $tunnelCount Aktif" -ForegroundColor Yellow
    Write-Host "Ana Panel Tunnel: İlk cloudflared penceresini kontrol edin" -ForegroundColor Yellow
    Write-Host "Kullanıcı Panel Tunnel: İkinci cloudflared penceresini kontrol edin" -ForegroundColor Yellow
}

# Port kontrolü
$port5000Check = netstat -an | Select-String ":5000.*LISTENING"
$port3000Check = netstat -an | Select-String ":3000.*LISTENING"

if ($port5000Check) {
    Write-Success "Port 5000 (Ana Panel): Dinleniyor"
} else {
    Write-Warning "Port 5000: Dinlenmiyor"
}

if ($port3000Check) {
    Write-Success "Port 3000 (Kullanıcı Paneli): Dinleniyor"
} else {
    Write-Warning "Port 3000: Dinlenmiyor"
}

Write-Host ""
Write-Success "Tüm işlemler tamamlandı!"
Write-Host ""

# Kullanım örnekleri
Write-Host "💡 Kullanım Örnekleri:" -ForegroundColor Yellow
Write-Host "- Sadece Web UI: .\start_all.ps1 -WebOnly" -ForegroundColor Gray
Write-Host "- Sadece Bot: .\start_all.ps1 -BotOnly" -ForegroundColor Gray
Write-Host "- Tunnel olmadan: .\start_all.ps1 -NoTunnel" -ForegroundColor Gray