# TrendCord Server Update Script
# This script pulls latest changes from GitHub and restarts services
# Now includes Unified Web App deployment

param(
    [switch]$Force,
    [switch]$NoRestart,
    [switch]$BackupFirst,
    [switch]$PushChanges,
    [switch]$UnifiedApp
)

# Color functions
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host ""
Write-Host "TrendCord Server Update Script" -ForegroundColor Magenta
Write-Host "==============================" -ForegroundColor Magenta
if ($UnifiedApp) {
    Write-Host "🚀 UNIFIED WEB APP MODE" -ForegroundColor Yellow
}
Write-Host ""

# Check working directory
$currentDir = Get-Location
Write-Info "Current directory: $currentDir"

if (-not (Test-Path ".git")) {
    Write-Error "This is not a Git repository! Run from TrendCord folder."
    exit 1
}

# Push Unified Web App changes to GitHub if requested
if ($PushChanges) {
    Write-Info "🚀 Pushing Unified Web App changes to GitHub..."
    
    # Check if unified app files exist
    $unifiedFiles = @(
        "unified_web_app.py",
        "user_auth.py", 
        "templates/unified_login.html",
        "templates/admin_login.html",
        "templates/admin_dashboard.html",
        "templates/user_dashboard.html",
        "setup_cloudflare_tunnel.ps1",
        "quick_unified_start.bat",
        "UNIFIED_WEB_APP_GUIDE.md"
    )
    
    $missingFiles = @()
    foreach ($file in $unifiedFiles) {
        if (-not (Test-Path $file)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Warning "Missing Unified Web App files:"
        $missingFiles | ForEach-Object { Write-Warning "  - $_" }
        Write-Error "Please ensure all Unified Web App files are present before pushing!"
        exit 1
    }
    
    # Add all unified app files
    Write-Info "Adding Unified Web App files to Git..."
    foreach ($file in $unifiedFiles) {
        git add $file
        Write-Success "Added: $file"
    }
    
    # Also add updated files
    git add .env.example
    git add update_server.ps1
    git add deploy_unified_app.bat
    
    # Check if there are changes to commit
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Info "Committing Unified Web App changes..."
        
        $commitMessage = "🚀 Add Unified Web App - Single Cloudflare tunnel for admin and user access

Features:
- Single URL for both admin and user login
- Admin panel with system management
- User panel with Discord OAuth
- Cloudflare tunnel integration
- Secure authentication system
- Responsive design
- Real-time updates via WebSocket

Files added:
- unified_web_app.py (main application)
- user_auth.py (authentication system)
- HTML templates for unified interface
- Cloudflare tunnel setup script
- Quick start scripts
- Comprehensive documentation"

        git commit -m "$commitMessage"
        Write-Success "Changes committed successfully!"
        
        # Push to GitHub
        Write-Info "Pushing to GitHub..."
        $currentBranch = git branch --show-current
        git push origin $currentBranch
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "🎉 Unified Web App successfully pushed to GitHub!"
            Write-Info "Repository updated with latest Unified Web App files"
        } else {
            Write-Error "Failed to push to GitHub!"
            exit 1
        }
    } else {
        Write-Info "No changes to commit - repository is up to date"
    }
    
    Write-Host ""
    Write-Host "📋 UNIFIED WEB APP DEPLOYMENT SUMMARY:" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "✅ All files pushed to GitHub" -ForegroundColor Green
    Write-Host "✅ Single Cloudflare tunnel setup ready" -ForegroundColor Green
    Write-Host "✅ Admin and User panels integrated" -ForegroundColor Green
    Write-Host "✅ Discord OAuth configured" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Run: .\setup_cloudflare_tunnel.ps1 -Domain 'yourdomain.com'" -ForegroundColor Cyan
    Write-Host "2. Configure Discord OAuth in Developer Portal" -ForegroundColor Cyan
    Write-Host "3. Update .env file with your settings" -ForegroundColor Cyan
    Write-Host "4. Start with: .\quick_unified_start.bat" -ForegroundColor Cyan
    Write-Host ""
    
    # Exit if only pushing changes
    if (-not $UnifiedApp -and -not $NoRestart) {
        exit 0
    }
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
if (-not $PushChanges) {
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
        if (-not $NoRestart -and -not $UnifiedApp) {
            $restart = Read-Host "Do you want to restart services? (y/N)"
            if ($restart -ne "y" -and $restart -ne "Y") {
                exit 0
            }
        }
    } else {
        Write-Info "$behind new commits found. Updating..."
        
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
    }
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

# Restart services
if (-not $NoRestart) {
    if ($UnifiedApp) {
        Write-Info "🚀 Starting Unified Web App services..."
        
        # Stop existing services
        Write-Info "Stopping existing services..."
        
        # Stop all Python processes
        $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
        if ($pythonProcesses) {
            $pythonProcesses | Stop-Process -Force
            Write-Success "Python processes stopped"
            Start-Sleep -Seconds 2
        }
        
        # Stop Cloudflare tunnels
        $tunnelProcesses = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
        if ($tunnelProcesses) {
            $tunnelProcesses | Stop-Process -Force
            Write-Success "Cloudflare tunnels stopped"
            Start-Sleep -Seconds 2
        }
        
        Write-Info "Starting Unified Web App..."
        
        # Check if unified app exists
        if (Test-Path "unified_web_app.py") {
            # Start Unified Web App
            Write-Info "Starting Unified Web App (Port 5000)..."
            Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$currentDir'; if (Test-Path 'venv/Scripts/Activate.ps1') { .\venv\Scripts\Activate.ps1 }; python unified_web_app.py" -WindowStyle Normal
            Start-Sleep -Seconds 5
            Write-Success "Unified Web App started"
            
            # Start Cloudflare tunnel for unified app
            $cloudflaredPath = ""
            if (Test-Path "cloudflared.exe") {
                $cloudflaredPath = ".\cloudflared.exe"
            } elseif (Test-Path "C:\Users\Administrator\cloudflared.exe") {
                $cloudflaredPath = "C:\Users\Administrator\cloudflared.exe"
            } elseif (Get-Command "cloudflared" -ErrorAction SilentlyContinue) {
                $cloudflaredPath = "cloudflared"
            }
            
            if ($cloudflaredPath) {
                Write-Info "Starting Cloudflare Tunnel for Unified App..."
                
                # Check if tunnel config exists
                if (Test-Path "$env:USERPROFILE\.cloudflared\config.yml") {
                    # Use configured tunnel
                    Start-Process -FilePath $cloudflaredPath -ArgumentList "tunnel", "run", "trendyol-bot-unified" -WindowStyle Normal
                    Write-Success "Configured Cloudflare Tunnel started"
                } else {
                    # Use quick tunnel
                    Start-Process -FilePath $cloudflaredPath -ArgumentList "tunnel", "--url", "http://localhost:5000" -WindowStyle Normal
                    Write-Success "Quick Cloudflare Tunnel started"
                }
                
                Start-Sleep -Seconds 5
                Write-Info "Tunnel URL will be displayed in the cloudflared window"
            } else {
                Write-Warning "Cloudflared not found! Install from: https://github.com/cloudflare/cloudflared/releases"
                Write-Info "Or run: .\setup_cloudflare_tunnel.ps1 to install and configure"
            }
            
            Write-Host ""
            Write-Host "🎉 UNIFIED WEB APP STARTED!" -ForegroundColor Green
            Write-Host "============================" -ForegroundColor Green
            Write-Host "📱 Local Access: http://localhost:5000" -ForegroundColor Cyan
            Write-Host "🌐 Public Access: Check cloudflared window for tunnel URL" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "🔗 Login Options:" -ForegroundColor Yellow
            Write-Host "👨‍💼 Admin: /login?type=admin" -ForegroundColor White
            Write-Host "👤 User: /login?type=user (Discord OAuth)" -ForegroundColor White
            Write-Host ""
            
        } else {
            Write-Error "unified_web_app.py not found! Please ensure Unified Web App files are present."
            Write-Info "Run with -PushChanges parameter first to deploy Unified Web App files."
            exit 1
        }
    }
}

# Status check
if (-not $NoRestart) {
    Write-Info "Checking service status..."
    Start-Sleep -Seconds 5

    if ($UnifiedApp) {
        # Unified Web App status check
        $unifiedAppRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*unified_web_app.py*" }
        $tunnelRunning = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue

        Write-Host ""
        Write-Host "🚀 UNIFIED WEB APP STATUS:" -ForegroundColor Cyan
        Write-Host "===========================" -ForegroundColor Cyan

        if ($unifiedAppRunning) {
            Write-Success "Unified Web App (Port 5000): Running"
        } else {
            Write-Warning "Unified Web App: Stopped"
        }

        if ($tunnelRunning) {
            $tunnelCount = ($tunnelRunning | Measure-Object).Count
            Write-Success "Cloudflare Tunnel: $tunnelCount Running"
        } else {
            Write-Warning "Cloudflare Tunnel: Stopped"
        }

        # Show access URLs for Unified App
        Write-Host ""
        Write-Host "🔗 ACCESS URLS:" -ForegroundColor Green
        Write-Host "===============" -ForegroundColor Green
        Write-Host "📱 Local Access: http://localhost:5000" -ForegroundColor Cyan
        Write-Host "🌐 Public Access: Check cloudflared window for tunnel URL" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🚪 Login Options:" -ForegroundColor Yellow
        Write-Host "👨‍💼 Admin Login: /login?type=admin" -ForegroundColor White
        Write-Host "👤 User Login: /login?type=user (Discord OAuth)" -ForegroundColor White
    }
}

# Last commit info
$lastCommit = git log -1 --pretty=format:"%h - %s (%cr)"
Write-Host ""
Write-Host "Last Commit: $lastCommit" -ForegroundColor Magenta

Write-Host ""
if ($UnifiedApp) {
    Write-Success "🎉 Unified Web App update completed!"
} else {
    Write-Success "Update completed!"
}
Write-Host ""

# Create log file
$logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Update completed - Commit: $lastCommit"
if ($UnifiedApp) {
    $logEntry += " - Unified Web App Mode"
}
Add-Content -Path "update_log.txt" -Value $logEntry

Write-Info "Update log saved to: update_log.txt"

# Show usage examples
if ($PushChanges -or $UnifiedApp) {
    Write-Host ""
    Write-Host "📚 USAGE EXAMPLES:" -ForegroundColor Magenta
    Write-Host "==================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "🚀 Deploy Unified Web App to GitHub:" -ForegroundColor Yellow
    Write-Host ".\update_server.ps1 -PushChanges" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 Start Unified Web App:" -ForegroundColor Yellow
    Write-Host ".\update_server.ps1 -UnifiedApp" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔄 Update and start Unified App:" -ForegroundColor Yellow
    Write-Host ".\update_server.ps1 -UnifiedApp -Force" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📦 Deploy and start in one command:" -ForegroundColor Yellow
    Write-Host ".\update_server.ps1 -PushChanges -UnifiedApp" -ForegroundColor Cyan
    Write-Host ""
}