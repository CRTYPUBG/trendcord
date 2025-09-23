# Port 3000 Sorun Çözme Scripti

Write-Host "🔍 Port 3000 durumu kontrol ediliyor..." -ForegroundColor Cyan

# Port 3000'i kullanan processleri bul
$port3000Processes = netstat -ano | Select-String ":3000" | ForEach-Object {
    $parts = $_.ToString().Split(' ', [StringSplitOptions]::RemoveEmptyEntries)
    if ($parts.Length -ge 5) {
        $pid = $parts[-1]
        try {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                [PSCustomObject]@{
                    PID = $pid
                    ProcessName = $process.ProcessName
                    CommandLine = $process.CommandLine
                }
            }
        } catch {
            [PSCustomObject]@{
                PID = $pid
                ProcessName = "Unknown"
                CommandLine = "N/A"
            }
        }
    }
}

if ($port3000Processes) {
    Write-Host "⚠️  Port 3000'i kullanan processler:" -ForegroundColor Yellow
    $port3000Processes | Format-Table -AutoSize
    
    $killProcesses = Read-Host "Bu processleri sonlandırmak ister misiniz? (y/N)"
    if ($killProcesses -eq "y" -or $killProcesses -eq "Y") {
        foreach ($proc in $port3000Processes) {
            try {
                Stop-Process -Id $proc.PID -Force
                Write-Host "✅ Process $($proc.PID) sonlandırıldı" -ForegroundColor Green
            } catch {
                Write-Host "❌ Process $($proc.PID) sonlandırılamadı: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "✅ Port 3000 boş" -ForegroundColor Green
}

# Kullanıcı panelini başlat
Write-Host "🚀 Kullanıcı paneli başlatılıyor..." -ForegroundColor Cyan
try {
    Start-Process -FilePath "python" -ArgumentList "start_user_panel.py" -NoNewWindow -PassThru
    Start-Sleep -Seconds 5
    
    # Kontrol et
    $userPanelRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_user_panel.py*" }
    if ($userPanelRunning) {
        Write-Host "✅ Kullanıcı paneli başlatıldı (PID: $($userPanelRunning.Id))" -ForegroundColor Green
        
        # Port kontrolü
        Start-Sleep -Seconds 2
        $portCheck = netstat -an | Select-String ":3000.*LISTENING"
        if ($portCheck) {
            Write-Host "✅ Port 3000 dinleniyor" -ForegroundColor Green
            Write-Host "🌐 Yerel erişim: http://localhost:3000" -ForegroundColor Cyan
        } else {
            Write-Host "⚠️  Port 3000 henüz dinlenmiyor, birkaç saniye bekleyin..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Kullanıcı paneli başlatılamadı" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Hata: $($_.Exception.Message)" -ForegroundColor Red
}