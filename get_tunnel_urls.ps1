# Cloudflare Tunnel URL'lerini Otomatik Yakalama Scripti

param(
    [switch]$Watch,
    [int]$Timeout = 30
)

function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Host ""
Write-Host "🔍 Cloudflare Tunnel URL Yakalayıcı" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Magenta
Write-Host ""

# Cloudflared processlerini bul
$cloudflaredProcesses = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue

if (-not $cloudflaredProcesses) {
    Write-Warning "Cloudflared process bulunamadı!"
    Write-Info "Önce tunnels başlatın: .\start_all.ps1"
    exit 1
}

$processCount = ($cloudflaredProcesses | Measure-Object).Count
Write-Info "$processCount Cloudflared process bulundu"

# Tunnel URL'lerini yakalamak için log dosyalarını kontrol et
$tunnelUrls = @()
$startTime = Get-Date

Write-Info "Tunnel URL'leri aranıyor... (Maksimum $Timeout saniye)"

do {
    # Windows Event Log'larını kontrol et (eğer varsa)
    try {
        $events = Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='cloudflared'} -MaxEvents 50 -ErrorAction SilentlyContinue
        foreach ($event in $events) {
            if ($event.Message -match 'https://[a-zA-Z0-9\-]+\.trycloudflare\.com') {
                $url = $matches[0]
                if ($url -notin $tunnelUrls) {
                    $tunnelUrls += $url
                }
            }
        }
    } catch {
        # Event log yoksa devam et
    }
    
    # Temp dosyalarını kontrol et
    $tempFiles = Get-ChildItem -Path $env:TEMP -Filter "*cloudflared*" -ErrorAction SilentlyContinue
    foreach ($file in $tempFiles) {
        try {
            $content = Get-Content $file.FullName -ErrorAction SilentlyContinue
            foreach ($line in $content) {
                if ($line -match 'https://[a-zA-Z0-9\-]+\.trycloudflare\.com') {
                    $url = $matches[0]
                    if ($url -notin $tunnelUrls) {
                        $tunnelUrls += $url
                    }
                }
            }
        } catch {
            # Dosya okunamıyorsa devam et
        }
    }
    
    # Eğer 2 URL bulduysak dur
    if ($tunnelUrls.Count -ge 2) {
        break
    }
    
    Start-Sleep -Seconds 2
    $elapsed = (Get-Date) - $startTime
    
} while ($elapsed.TotalSeconds -lt $Timeout)

# Sonuçları göster
Write-Host ""
Write-Host "📋 Bulunan Tunnel URL'leri:" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green

if ($tunnelUrls.Count -eq 0) {
    Write-Warning "Hiç tunnel URL'si bulunamadı!"
    Write-Info "Manuel kontrol için:"
    Write-Info "1. Cloudflared pencerelerini kontrol edin"
    Write-Info "2. 'Your quick Tunnel has been created!' mesajını arayın"
} else {
    for ($i = 0; $i -lt $tunnelUrls.Count; $i++) {
        $panelName = if ($i -eq 0) { "Ana Panel (Port 5000)" } else { "Kullanıcı Paneli (Port 3000)" }
        Write-Success "$panelName: $($tunnelUrls[$i])"
    }
}

# .env dosyasını güncelle (kullanıcı paneli için)
if ($tunnelUrls.Count -ge 2) {
    $userPanelUrl = $tunnelUrls[1]  # İkinci tunnel kullanıcı paneli için
    $redirectUri = "$userPanelUrl/auth/callback"
    
    Write-Host ""
    Write-Host "🔧 Discord OAuth Ayarları:" -ForegroundColor Yellow
    Write-Host "=========================" -ForegroundColor Yellow
    Write-Host "Redirect URI: $redirectUri" -ForegroundColor Cyan
    
    $updateEnv = Read-Host "Bu redirect URI'yi .env dosyasına kaydetmek ister misiniz? (y/N)"
    if ($updateEnv -eq "y" -or $updateEnv -eq "Y") {
        try {
            $envContent = Get-Content ".env" -ErrorAction SilentlyContinue
            $newEnvContent = @()
            $updated = $false
            
            foreach ($line in $envContent) {
                if ($line -match '^DISCORD_REDIRECT_URI=') {
                    $newEnvContent += "DISCORD_REDIRECT_URI=$redirectUri"
                    $updated = $true
                } else {
                    $newEnvContent += $line
                }
            }
            
            if (-not $updated) {
                $newEnvContent += "DISCORD_REDIRECT_URI=$redirectUri"
            }
            
            $newEnvContent | Set-Content ".env"
            Write-Success ".env dosyası güncellendi!"
        } catch {
            Write-Error ".env dosyası güncellenemedi: $($_.Exception.Message)"
        }
    }
}

# Watch modu
if ($Watch) {
    Write-Host ""
    Write-Info "Watch modu aktif. Yeni tunnel'lar için izleniyor... (Ctrl+C ile çıkış)"
    
    while ($true) {
        Start-Sleep -Seconds 10
        
        $newProcesses = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
        $newCount = if ($newProcesses) { ($newProcesses | Measure-Object).Count } else { 0 }
        
        if ($newCount -ne $processCount) {
            Write-Info "Cloudflared process sayısı değişti: $processCount -> $newCount"
            $processCount = $newCount
            
            if ($newCount -eq 0) {
                Write-Warning "Tüm tunnel'lar kapandı!"
            }
        }
    }
}

Write-Host ""
Write-Success "Tunnel URL yakalama tamamlandı!"
Write-Host ""