# 🪟 Windows Kurulum Rehberi

## 📋 **Chocolatey ile Gerekli Araçları Kurma**

### 1️⃣ **Chocolatey Kurulumu**
PowerShell'i **Yönetici olarak** açın ve şu komutu çalıştırın:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 2️⃣ **Gerekli Araçları Kurma**
```powershell
# Curl kurulumu
choco install curl -y

# Git kurulumu (eğer yoksa)
choco install git -y

# Python kurulumu (eğer yoksa)
choco install python -y

# Node.js kurulumu (opsiyonel)
choco install nodejs -y

# SSH client (OpenSSH)
choco install openssh -y

# Putty (SSH için alternatif)
choco install putty -y

# Visual Studio Code (kod editörü)
choco install vscode -y

# Windows Terminal (modern terminal)
choco install microsoft-windows-terminal -y
```

### 3️⃣ **Kurulum Doğrulama**
```powershell
# Curl test
curl --version

# Git test
git --version

# Python test
python --version

# SSH test
ssh -V
```

## 🚀 **TrendCord'u Windows'ta Çalıştırma**

### 1️⃣ **Repository Klonlama**
```powershell
# Masaüstüne git
cd $env:USERPROFILE\Desktop

# Repository klonla
git clone https://github.com/CRTYPUBG/trendcord.git
cd trendcord
```

### 2️⃣ **Python Virtual Environment**
```powershell
# Virtual environment oluştur
python -m venv venv

# Aktive et
.\venv\Scripts\Activate.ps1

# Gereksinimler kur
pip install -r requirements.txt
```

### 3️⃣ **Yapılandırma**
```powershell
# .env dosyası oluştur
copy .env.example .env

# Notepad ile düzenle
notepad .env
```

### 4️⃣ **Çalıştırma**
```powershell
# Discord Bot
python main.py

# Web UI (yeni terminal)
python start_web_ui.py
```

## 🔧 **Windows Batch Scriptleri**

### 📄 **start_bot.bat**
```batch
@echo off
echo 🤖 TrendCord Discord Bot Başlatılıyor...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py
pause
```

### 📄 **start_web.bat**
```batch
@echo off
echo 🌐 TrendCord Web UI Başlatılıyor...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python start_web_ui.py
pause
```

### 📄 **update.bat**
```batch
@echo off
echo 🔄 TrendCord Güncelleniyor...
cd /d "%~dp0"
git pull origin main
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo ✅ Güncelleme tamamlandı!
pause
```

### 📄 **install.bat**
```batch
@echo off
echo 🚀 TrendCord Kurulumu Başlıyor...

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı! Lütfen Python'u kurun.
    echo 📥 https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Virtual environment oluştur
echo 📦 Virtual environment oluşturuluyor...
python -m venv venv

REM Aktive et
echo 🔧 Virtual environment aktive ediliyor...
call venv\Scripts\activate.bat

REM Gereksinimler kur
echo 📚 Gereksinimler kuruluyor...
pip install --upgrade pip
pip install -r requirements.txt

REM .env dosyası oluştur
if not exist .env (
    echo 📝 .env dosyası oluşturuluyor...
    copy .env.example .env
    echo ⚠️  ÖNEMLI: .env dosyasını düzenlemeyi unutmayın!
    echo 🔑 Discord token'ınızı ekleyin.
)

REM Veri klasörleri oluştur
if not exist data mkdir data
if not exist logs mkdir logs

echo ✅ Kurulum tamamlandı!
echo 📋 Sonraki adımlar:
echo    1. .env dosyasını düzenleyin
echo    2. start_bot.bat ile bot'u başlatın
echo    3. start_web.bat ile web UI'yi başlatın
pause
```

## 🔗 **EC2'ye Bağlanma (Windows'tan)**

### 1️⃣ **SSH ile Bağlanma**
```powershell
# OpenSSH ile
ssh -i "path\to\your-key.pem" ubuntu@YOUR_EC2_IP

# Örnek
ssh -i "C:\Users\YourName\Downloads\my-key.pem" ubuntu@172.31.31.154
```

### 2️⃣ **PuTTY ile Bağlanma**
1. PuTTY'yi açın
2. Host Name: `ubuntu@YOUR_EC2_IP`
3. Port: `22`
4. Connection Type: `SSH`
5. Auth > Private key file: `.pem` dosyanızı seçin
6. Open'a tıklayın

### 3️⃣ **Windows Terminal ile**
```powershell
# Windows Terminal'de yeni profil oluşturun
{
    "name": "EC2 TrendCord",
    "commandline": "ssh -i \"C:\\path\\to\\key.pem\" ubuntu@YOUR_EC2_IP",
    "icon": "🚀"
}
```

## 🛠️ **EC2'de Hızlı Kurulum (Windows'tan)**

### 1️⃣ **Tek Komutla Kurulum**
```powershell
# EC2'ye SSH ile bağlandıktan sonra
curl -sSL https://raw.githubusercontent.com/CRTYPUBG/trendcord/main/quick_ec2_setup.sh | bash
```

### 2️⃣ **Manuel Kurulum**
```bash
# Sistem güncelleme
sudo apt update && sudo apt upgrade -y

# Repository klonlama
cd /home/ubuntu
git clone https://github.com/CRTYPUBG/trendcord.git
cd trendcord

# Kurulum scripti çalıştır
chmod +x quick_ec2_setup.sh
./quick_ec2_setup.sh
```

## 📊 **Windows'ta Geliştirme Ortamı**

### 🔧 **VS Code Ayarları**
```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/venv": true,
        "**/.git": true
    }
}
```

### 🐛 **Debug Yapılandırması**
```json
{
    "name": "TrendCord Bot",
    "type": "python",
    "request": "launch",
    "program": "main.py",
    "console": "integratedTerminal",
    "env": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```

## 🚨 **Windows Sorun Giderme**

### ❌ **PowerShell Execution Policy Hatası**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ **Python Bulunamadı**
```powershell
# Python PATH kontrolü
$env:PATH -split ';' | Where-Object { $_ -like '*Python*' }

# Manuel PATH ekleme
$env:PATH += ";C:\Python311;C:\Python311\Scripts"
```

### ❌ **Git Bulunamadı**
```powershell
# Git kurulumu
choco install git -y

# PATH yenileme
refreshenv
```

### ❌ **Port Kullanımda Hatası**
```powershell
# Port 5000 kontrolü
netstat -ano | findstr :5000

# Process sonlandırma
taskkill /PID <PID_NUMBER> /F
```

## 🎯 **Hızlı Başlangıç Komutları**

### 📥 **Chocolatey Kurulum (Tek Komut)**
```powershell
# PowerShell'i Yönetici olarak açın ve çalıştırın:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 🛠️ **Gerekli Araçlar (Tek Komut)**
```powershell
choco install curl git python nodejs openssh vscode microsoft-windows-terminal -y
```

### 🚀 **TrendCord Kurulum (Tek Komut)**
```powershell
cd $env:USERPROFILE\Desktop; git clone https://github.com/CRTYPUBG/trendcord.git; cd trendcord; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; copy .env.example .env; echo "✅ Kurulum tamamlandı! .env dosyasını düzenleyin."
```

## 🌐 **Erişim URL'leri**

### 🔗 **Yerel Geliştirme**
- **Web UI**: `http://localhost:5000`
- **Dashboard**: `http://127.0.0.1:5000`

### 🔗 **EC2 Erişimi**
- **Doğrudan**: `http://YOUR_EC2_IP:5000`
- **Nginx**: `http://YOUR_EC2_IP`

---

**🎉 Windows'ta TrendCord geliştirme ortamı hazır!**