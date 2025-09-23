# TrendCord Server Update Script
# This script pulls latest changes from GitHub and restarts services

param(
    [switch]$Force,
    [switch]$NoRestart,
    [switch]$BackupFirst
)

# Color functions
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host ""
Write-Host "TrendCord Server Update Script" -ForegroundColor Magenta
Write-Host "==============================" -ForegroundColor Magenta
Write-Host ""

# Check working directory
$currentDir = Get-Location
Write-Info "Current directory: $currentDir"

if (-not (Test-Path ".git")) {
    Write-Error "This is not a Git repository! Run from TrendCord folder."
    exit 1
}

# Create backup
if ($BackupFirst) {
    Write-Info "Creating backup..."
    $backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    
    try {
        # Database backup
        if (Test-Path "data/trendyol_tracker.sqlite") {
            New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
            Copy-Item "data/trendyol_tracker.sqlite" "$backupDir/database_backup.sqlite"
            Write-Success "Database backup created: $backupDir/database_backup.sqlite"
        }
        
        # .env backup
        if (Test-Path ".env") {
            Copy-Item ".env" "$backupDir/.env_backup"
            Write-Success "Configuration backup created: $backupDir/.env_backup"
        }
    }
    catch {
        Write-Warning "Error creating backup: $($_.Exception.Message)"
    }
}

# Check Git status
Write-Info "Checking Git status..."
$gitStatus = git status --porcelain
if ($gitStatus -and -not $Force) {
    Write-Warning "Local changes detected:"
    git status --short
    Write-Warning "Use -Force parameter to continue"
    exit 1
}

# Get current branch
$currentBranch = git branch --show-current
Write-Info "Current branch: $currentBranch"

# Fetch latest changes from remote
Write-Info "Fetching latest changes from GitHub..."
try {
    git fetch origin
    Write-Success "Fetch completed"
}
catch {
    Write-Error "Fetch failed: $($_.Exception.Message)"
    exit 1
}

# Check for changes
$behind = git rev-list --count HEAD..origin/$currentBranch
if ($behind -eq "0") {
    Write-Success "Server is already up to date! No update needed."
    if (-not $NoRestart) {
        $restart = Read-Host "Do you want to restart services? (y/N)"
        if ($restart -eq "y" -or $restart -eq "Y") {
            # Go to restart services section
        } else {
            exit 0
        }
    } else {
        exit 0
    }
} else {
    Write-Info "$behind new commits found. Updating..."
}

# Pull changes
Write-Info "Pulling changes..."
try {
    if ($Force -and $gitStatus) {
        Write-Warning "Resetting local changes..."
        git reset --hard HEAD
    }
    
    git pull origin $currentBranch
    Write-Success "Pull completed"
}
catch {
    Write-Error "Pull failed: $($_.Exception.Message)"
    exit 1
}

# Check virtual environment
if (Test-Path "venv/Scripts/Activate.ps1") {
    Write-Info "Activating virtual environment..."
    & "venv/Scripts/Activate.ps1"
    
    # Update requirements
    Write-Info "Updating Python packages..."
    try {
        pip install -r requirements.txt --upgrade
        Write-Success "Python packages updated"
    }
    catch {
        Write-Warning "Package update error: $($_.Exception.Message)"
    }
} else {
    Write-Warning "Virtual environment not found!"
}

# Database migration (if needed)
Write-Info "Checking database..."
if (Test-Path "database_migrations.py") {
    try {
        python database_migrations.py
        Write-Success "Database migrations applied"
    }
    catch {
        Write-Warning "Migration error: $($_.Exception.Message)"
    }
}

# Restart services
if (-not $NoRestart) {
    Write-Info "Restarting services..."
    
    # Discord Bot service
    Write-Info "Stopping Discord Bot..."
    $botProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    if ($botProcesses) {
        $botProcesses | Stop-Process -Force
        Write-Success "Discord Bot stopped"
        Start-Sleep -Seconds 2
    }
    
    # Web UI service
    Write-Info "Stopping Web UI..."
    $webProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
    if ($webProcesses) {
        $webProcesses | Stop-Process -Force
        Write-Success "Web UI stopped"
        Start-Sleep -Seconds 2
    }
    
    # Cloudflare tunnel stopping
    Write-Info "Stopping Cloudflare Tunnel..."
    $tunnelProcesses = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
    if ($tunnelProcesses) {
        $tunnelProcesses | Stop-Process -Force
        Write-Success "Cloudflare Tunnel stopped"
        Start-Sleep -Seconds 2
    }
    
    Write-Info "Starting services..."
    
    # Start Web UI
    Write-Info "Starting Web UI..."
    Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python start_web_ui.py --port 5000 --host 127.0.0.1" -WindowStyle Minimized
    Start-Sleep -Seconds 3
    
    # Start Cloudflare Tunnel
    $cloudflaredPath = ""
    if (Test-Path "cloudflared.exe") {
        $cloudflaredPath = ".\cloudflared.exe"
    } elseif (Test-Path "C:\Users\Administrator\cloudflared.exe") {
        $cloudflaredPath = "C:\Users\Administrator\cloudflared.exe"
    }
    
    if ($cloudflaredPath) {
        Write-Info "Starting Cloudflare Tunnel..."
        Start-Process -FilePath $cloudflaredPath -ArgumentList "tunnel", "--url", "http://localhost:5000" -WindowStyle Minimized
        Start-Sleep -Seconds 3
        Write-Success "Cloudflare Tunnel started"
    } else {
        Write-Warning "Cloudflared.exe not found!"
    }
    
    # Start Discord Bot (optional)
    $startBot = Read-Host "Do you want to start Discord Bot too? (y/N)"
    if ($startBot -eq "y" -or $startBot -eq "Y") {
        Write-Info "Starting Discord Bot..."
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; .\venv\Scripts\Activate.ps1; python main.py" -WindowStyle Minimized
        Write-Success "Discord Bot started"
    }
}

# Status check
Write-Info "Checking service status..."
Start-Sleep -Seconds 5

$webRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*start_web_ui.py*" }
$tunnelRunning = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
$botRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

Write-Host ""
Write-Host "Service Status:" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

if ($webRunning) {
    Write-Success "Web UI: Running"
} else {
    Write-Warning "Web UI: Stopped"
}

if ($tunnelRunning) {
    Write-Success "Cloudflare Tunnel: Running"
} else {
    Write-Warning "Cloudflare Tunnel: Stopped"
}

if ($botRunning) {
    Write-Success "Discord Bot: Running"
} else {
    Write-Info "Discord Bot: Stopped (can be started manually)"
}

# Show access URLs
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Green
Write-Host "============" -ForegroundColor Green

if ($tunnelRunning) {
    Write-Host "Cloudflare Tunnel: Check tunnel logs for URL" -ForegroundColor Yellow
}

Write-Host "Local: http://localhost:5000" -ForegroundColor Cyan

# Last commit info
$lastCommit = git log -1 --pretty=format:"%h - %s (%cr)"
Write-Host ""
Write-Host "Last Commit: $lastCommit" -ForegroundColor Magenta

Write-Host ""
Write-Success "Update completed!"
Write-Host ""

# Create log file
$logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Update completed - Commit: $lastCommit"
Add-Content -Path "update_log.txt" -Value $logEntry

Write-Info "Update log saved to: update_log.txt"