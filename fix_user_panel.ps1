# Kullanıcı Paneli Hızlı Çözüm Scripti

param(
    [switch]$Force,
    [switch]$Debug
)

function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Host ""
Write-Host "🔧 Kullanıcı Paneli Hızlı Çözüm" -ForegroundColor Magenta
Write-Host "===============================" -ForegroundColor Magenta
Write-Host ""

# 1. Mevcut durumu kontrol et
Write-Info "1. Mevcut durum kontrol ediliyor..."

$userPanelProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_user_panel*" }
$port3000 = netstat -an | Select-String ":3000.*LISTENING"

if ($userPanelProcess) {
    Write-Warning "Kullanıcı paneli zaten çalışıyor (PID: $($userPanelProcess.Id))"
    if ($Force) {
        Write-Info "Force modu: Mevcut process sonlandırılıyor..."
        $userPanelProcess | Stop-Process -Force
        Start-Sleep -Seconds 3
    } else {
        $restart = Read-Host "Yeniden başlatmak ister misiniz? (y/N)"
        if ($restart -eq "y" -or $restart -eq "Y") {
            $userPanelProcess | Stop-Process -Force
            Start-Sleep -Seconds 3
        } else {
            Write-Info "Mevcut process korunuyor"
            exit 0
        }
    }
}

if ($port3000) {
    Write-Success "Port 3000 dinleniyor"
} else {
    Write-Warning "Port 3000 dinlenmiyor"
}

# 2. Gereksinimler kontrolü
Write-Info "2. Gereksinimler kontrol ediliyor..."

$requiredFiles = @("start_user_panel.py", "user_web_ui.py", "user_auth.py", ".env")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Success "$file mevcut"
    } else {
        Write-Error "$file bulunamadı!"
        exit 1
    }
}

# 3. .env dosyası kontrolü
Write-Info "3. .env dosyası kontrol ediliyor..."

$envContent = Get-Content ".env" -ErrorAction SilentlyContinue
$requiredVars = @("DISCORD_CLIENT_ID", "DISCORD_CLIENT_SECRET", "FLASK_SECRET_KEY")

foreach ($var in $requiredVars) {
    $found = $envContent | Select-String "^$var="
    if ($found) {
        Write-Success "$var ayarlanmış"
    } else {
        Write-Error "$var eksik!"
    }
}

# 4. Python kütüphaneleri kontrolü
Write-Info "4. Python kütüphaneleri kontrol ediliyor..."

$requiredPackages = @("flask", "flask_cors", "flask_socketio", "cryptography")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        $result = python -c "import $package; print('OK')" 2>$null
        if ($result -eq "OK") {
            Write-Success "$package mevcut"
        } else {
            $missingPackages += $package
        }
    } catch {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Warning "Eksik kütüphaneler: $($missingPackages -join ', ')"
    Write-Info "Kütüphaneler yükleniyor..."
    pip install $($missingPackages -join ' ')
}

# 5. Port temizleme
Write-Info "5. Port 3000 temizleniyor..."

$port3000Processes = netstat -ano | Select-String ":3000" | ForEach-Object {
    $parts = $_.ToString().Split(' ', [StringSplitOptions]::RemoveEmptyEntries)
    if ($parts.Length -ge 5) {
        $pid = $parts[-1]
        try {
            Get-Process -Id $pid -ErrorAction SilentlyContinue
        } catch { $null }
    }
} | Where-Object { $_ -ne $null }

if ($port3000Processes) {
    Write-Warning "Port 3000'i kullanan processler bulundu"
    foreach ($proc in $port3000Processes) {
        if ($proc.ProcessName -ne "python" -or $proc.CommandLine -notlike "*start_user_panel*") {
            Write-Info "Process sonlandırılıyor: $($proc.ProcessName) (PID: $($proc.Id))"
            try {
                Stop-Process -Id $proc.Id -Force
            } catch {
                Write-Warning "Process sonlandırılamadı: $($proc.Id)"
            }
        }
    }
    Start-Sleep -Seconds 2
}

# 6. Kullanıcı panelini başlat
Write-Info "6. Kullanıcı paneli başlatılıyor..."

if ($Debug) {
    Write-Info "Debug modunda başlatılıyor (konsol görünür)..."
    Start-Process -FilePath "python" -ArgumentList "start_user_panel.py" -NoNewWindow -Wait
} else {
    Write-Info "Arka planda başlatılıyor..."
    $process = Start-Process -FilePath "python" -ArgumentList "start_user_panel.py" -WindowStyle Hidden -PassThru
    
    # 10 saniye bekle ve kontrol et
    Start-Sleep -Seconds 10
    
    $userPanelCheck = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_user_panel*" }
    $portCheck = netstat -an | Select-String ":3000.*LISTENING"
    
    if ($userPanelCheck -and $portCheck) {
        Write-Success "Kullanıcı paneli başarıyla başlatıldı!"
        Write-Success "PID: $($userPanelCheck.Id)"
        Write-Success "Port 3000: Dinleniyor"
        Write-Info "Yerel erişim: http://localhost:3000"
        
        # Tunnel kontrolü
        $tunnelProcesses = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
        if ($tunnelProcesses) {
            $tunnelCount = ($tunnelProcesses | Measure-Object).Count
            Write-Info "Cloudflare Tunnels: $tunnelCount aktif"
            Write-Info "Tunnel URL'lerini görmek için: .\get_tunnel_urls.ps1"
        }
    } else {
        Write-Error "Kullanıcı paneli başlatılamadı!"
        Write-Info "Debug için: .\fix_user_panel.ps1 -Debug"
    }
}

Write-Host ""
Write-Success "Kullanıcı paneli çözüm scripti tamamlandı!"
Write-Host ""