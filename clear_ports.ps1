# Port Temizleme Scripti

Write-Host "🔧 Port Temizleme Başlatılıyor..." -ForegroundColor Cyan

# Kontrol edilecek portlar
$ports = @(3000, 3001, 5000, 8080)

foreach ($port in $ports) {
    Write-Host "Port $port kontrol ediliyor..." -ForegroundColor Yellow
    
    # Port kullanan process'leri bul
    $processes = netstat -ano | Select-String ":$port " | ForEach-Object {
        $parts = $_.ToString().Split(' ', [StringSplitOptions]::RemoveEmptyEntries)
        if ($parts.Length -ge 5) {
            $pid = $parts[-1]
            try {
                Get-Process -Id $pid -ErrorAction SilentlyContinue
            } catch { $null }
        }
    } | Where-Object { $_ -ne $null }
    
    if ($processes) {
        Write-Host "Port $port kullanımda:" -ForegroundColor Red
        foreach ($proc in $processes) {
            Write-Host "  - $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Gray
            
            # Process'i sonlandır
            try {
                Stop-Process -Id $proc.Id -Force
                Write-Host "    ✅ Sonlandırıldı" -ForegroundColor Green
            } catch {
                Write-Host "    ❌ Sonlandırılamadı" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "Port $port boş ✅" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🎯 Port Temizleme Tamamlandı!" -ForegroundColor Green

# Son durum
Write-Host ""
Write-Host "📊 Port Durumu:" -ForegroundColor Cyan
foreach ($port in $ports) {
    $check = netstat -an | Select-String ":$port.*LISTENING"
    if ($check) {
        Write-Host "Port $port: Kullanımda ⚠️" -ForegroundColor Yellow
    } else {
        Write-Host "Port $port: Boş ✅" -ForegroundColor Green
    }
}