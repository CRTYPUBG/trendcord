# 🚀 AWS EC2 Deployment Rehberi

## 📋 **Ön Hazırlık**

### 🔧 **EC2 Instance Gereksinimleri**
- **Instance Type**: t3.small veya daha büyük (minimum 2GB RAM)
- **OS**: Ubuntu 20.04 LTS veya Amazon Linux 2
- **Storage**: 20GB+ SSD
- **Security Group**: HTTP (80), HTTPS (443), SSH (22), Custom (5000)

### 🔐 **Security Group Ayarları**
```
Type            Protocol    Port Range    Source
SSH             TCP         22           Your IP
HTTP            TCP         80           0.0.0.0/0
HTTPS           TCP         443          0.0.0.0/0
Custom TCP      TCP         5000         0.0.0.0/0
Custom TCP      TCP         8080         0.0.0.0/0
```

## 🛠️ **Sunucu Kurulumu**

### 1️⃣ **SSH ile Bağlanma**
```bash
# Windows'ta (PowerShell)
ssh -i "your-key.pem" ubuntu@172.31.31.154

# veya EC2 public IP ile
ssh -i "your-key.pem" ubuntu@YOUR_PUBLIC_IP
```

### 2️⃣ **Sistem Güncellemesi**
```bash
sudo apt update && sudo apt upgrade -y
```

### 3️⃣ **Python ve Git Kurulumu**
```bash
# Python 3.11 kurulumu
sudo apt install -y python3.11 python3.11-pip python3.11-venv git curl

# Python alternatiflerini ayarla
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1
```

### 4️⃣ **Node.js Kurulumu (Web UI için)**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 📦 **Proje Kurulumu**

### 1️⃣ **Repository Klonlama**
```bash
cd /home/ubuntu
git clone https://github.com/CRTYPUBG/trendcord.git
cd trendcord
```

### 2️⃣ **Virtual Environment Oluşturma**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ **Gereksinimler Kurulumu**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ **Yapılandırma Dosyası**
```bash
cp .env.example .env
nano .env
```

**.env dosyasını düzenleyin:**
```env
# Discord Bot Token
DISCORD_TOKEN=YOUR_ACTUAL_DISCORD_TOKEN

# Bot Ayarları
PREFIX=!
CHECK_INTERVAL=3600
PROXY_ENABLED=False
VERIFY_SSL=True

# Veritabanı
DATABASE_PATH=data/trendyol_tracker.sqlite

# Web UI
FLASK_SECRET_KEY=your-super-secret-key-here

# Admin ID'leri
GLOBAL_ADMIN_IDS=YOUR_DISCORD_USER_ID

# Sunucu Ayarları
HOST=0.0.0.0
PORT=5000
```

## 🔧 **Systemd Service Kurulumu**

### 1️⃣ **Discord Bot Service**
```bash
sudo nano /etc/systemd/system/trendcord-bot.service
```

```ini
[Unit]
Description=TrendCord Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/trendcord
Environment=PATH=/home/ubuntu/trendcord/venv/bin
ExecStart=/home/ubuntu/trendcord/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2️⃣ **Web UI Service**
```bash
sudo nano /etc/systemd/system/trendcord-web.service
```

```ini
[Unit]
Description=TrendCord Web UI
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/trendcord
Environment=PATH=/home/ubuntu/trendcord/venv/bin
ExecStart=/home/ubuntu/trendcord/venv/bin/python start_web_ui.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3️⃣ **Servisleri Etkinleştirme**
```bash
sudo systemctl daemon-reload
sudo systemctl enable trendcord-bot
sudo systemctl enable trendcord-web
sudo systemctl start trendcord-bot
sudo systemctl start trendcord-web
```

## 🌐 **Nginx Reverse Proxy (Opsiyonel)**

### 1️⃣ **Nginx Kurulumu**
```bash
sudo apt install -y nginx
```

### 2️⃣ **Nginx Yapılandırması**
```bash
sudo nano /etc/nginx/sites-available/trendcord
```

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3️⃣ **Nginx Etkinleştirme**
```bash
sudo ln -s /etc/nginx/sites-available/trendcord /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 **SSL Sertifikası (Let's Encrypt)**

### 1️⃣ **Certbot Kurulumu**
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2️⃣ **SSL Sertifikası Alma**
```bash
sudo certbot --nginx -d YOUR_DOMAIN
```

## 📊 **Monitoring ve Yönetim**

### 🔍 **Servis Durumu Kontrol**
```bash
# Bot durumu
sudo systemctl status trendcord-bot

# Web UI durumu
sudo systemctl status trendcord-web

# Logları görüntüleme
sudo journalctl -u trendcord-bot -f
sudo journalctl -u trendcord-web -f
```

### 🔄 **Servis Yönetimi**
```bash
# Servisleri yeniden başlatma
sudo systemctl restart trendcord-bot
sudo systemctl restart trendcord-web

# Servisleri durdurma
sudo systemctl stop trendcord-bot
sudo systemctl stop trendcord-web

# Servisleri başlatma
sudo systemctl start trendcord-bot
sudo systemctl start trendcord-web
```

### 📈 **Sistem Kaynaklarını İzleme**
```bash
# CPU ve RAM kullanımı
htop

# Disk kullanımı
df -h

# Ağ bağlantıları
netstat -tulpn | grep :5000
```

## 🔧 **Güncelleme Prosedürü**

### 1️⃣ **Kod Güncelleme**
```bash
cd /home/ubuntu/trendcord
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ **Servisleri Yeniden Başlatma**
```bash
sudo systemctl restart trendcord-bot
sudo systemctl restart trendcord-web
```

## 🛡️ **Güvenlik Ayarları**

### 1️⃣ **Firewall Yapılandırması**
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000
```

### 2️⃣ **Fail2Ban Kurulumu**
```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 🔄 **Otomatik Backup**

### 1️⃣ **Backup Script Oluşturma**
```bash
nano /home/ubuntu/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

# Veritabanı backup
cp /home/ubuntu/trendcord/data/trendyol_tracker.sqlite $BACKUP_DIR/db_backup_$DATE.sqlite

# Eski backupları temizle (30 günden eski)
find $BACKUP_DIR -name "*.sqlite" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 2️⃣ **Crontab Ayarlama**
```bash
chmod +x /home/ubuntu/backup.sh
crontab -e

# Her gün saat 02:00'da backup al
0 2 * * * /home/ubuntu/backup.sh
```

## 🌍 **Erişim URL'leri**

### 🔗 **Doğrudan Erişim**
- **Web UI**: `http://YOUR_EC2_PUBLIC_IP:5000`
- **Nginx ile**: `http://YOUR_DOMAIN_OR_IP`
- **SSL ile**: `https://YOUR_DOMAIN`

### 📱 **Mobil Erişim**
- Responsive tasarım sayesinde mobil cihazlardan erişilebilir
- PWA desteği için manifest.json eklenebilir

## 🚨 **Sorun Giderme**

### ❌ **Yaygın Sorunlar**

**1. Port 5000 erişilemiyor:**
```bash
# Security Group'ta port 5000'in açık olduğunu kontrol edin
# Firewall ayarlarını kontrol edin
sudo ufw status
```

**2. Bot çalışmıyor:**
```bash
# Token'ın doğru olduğunu kontrol edin
# Logları kontrol edin
sudo journalctl -u trendcord-bot -n 50
```

**3. Veritabanı hatası:**
```bash
# Dosya izinlerini kontrol edin
ls -la /home/ubuntu/trendcord/data/
chmod 755 /home/ubuntu/trendcord/data/
```

### 🔧 **Debug Komutları**
```bash
# Portları kontrol et
sudo netstat -tulpn | grep :5000

# Servis logları
sudo journalctl -u trendcord-web --since "1 hour ago"

# Sistem kaynakları
free -h
df -h
```

## 📞 **Destek**

### 🆘 **Yardım Alma**
- GitHub Issues: https://github.com/CRTYPUBG/trendcord/issues
- Discord sunucusunda `/yardim` komutu
- Logları paylaşırken hassas bilgileri gizleyin

---

**🎉 EC2'de TrendCord başarıyla çalışıyor!**

*Bu rehber AWS EC2 Ubuntu 20.04 LTS için optimize edilmiştir.*