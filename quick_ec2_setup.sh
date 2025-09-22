#!/bin/bash

# 🚀 TrendCord EC2 Hızlı Kurulum Scripti
# Bu script AWS EC2 Ubuntu sunucusunda TrendCord'u otomatik kurar

set -e

echo "🚀 TrendCord EC2 Kurulumu Başlıyor..."
echo "======================================"

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonksiyonlar
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Root kontrolü
if [ "$EUID" -eq 0 ]; then
    print_error "Bu scripti root kullanıcısı ile çalıştırmayın!"
    exit 1
fi

# 1. Sistem güncellemesi
print_status "Sistem güncelleniyor..."
sudo apt update && sudo apt upgrade -y
print_success "Sistem güncellendi"

# 2. Gerekli paketleri kur
print_status "Gerekli paketler kuruluyor..."
sudo apt install -y python3.11 python3.11-pip python3.11-venv git curl htop nginx ufw fail2ban
print_success "Paketler kuruldu"

# 3. Python alternatiflerini ayarla
print_status "Python ayarları yapılıyor..."
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1
print_success "Python ayarlandı"

# 4. Repository klonla
print_status "TrendCord repository klonlanıyor..."
cd /home/ubuntu
if [ -d "trendcord" ]; then
    print_warning "TrendCord klasörü zaten mevcut, güncelleniyor..."
    cd trendcord
    git pull origin main
else
    git clone https://github.com/CRTYPUBG/trendcord.git
    cd trendcord
fi
print_success "Repository hazır"

# 5. Virtual environment oluştur
print_status "Virtual environment oluşturuluyor..."
python3 -m venv venv
source venv/bin/activate
print_success "Virtual environment oluşturuldu"

# 6. Python paketlerini kur
print_status "Python paketleri kuruluyor..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python paketleri kuruldu"

# 7. Yapılandırma dosyası oluştur
print_status "Yapılandırma dosyası oluşturuluyor..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning ".env dosyası oluşturuldu. Lütfen Discord token'ınızı ekleyin!"
    print_warning "nano .env komutu ile düzenleyebilirsiniz."
else
    print_success ".env dosyası zaten mevcut"
fi

# 8. Veri klasörü oluştur
print_status "Veri klasörleri oluşturuluyor..."
mkdir -p data logs
chmod 755 data logs
print_success "Veri klasörleri hazır"

# 9. Systemd servisleri oluştur
print_status "Systemd servisleri oluşturuluyor..."

# Discord Bot Service
sudo tee /etc/systemd/system/trendcord-bot.service > /dev/null <<EOF
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
EOF

# Web UI Service
sudo tee /etc/systemd/system/trendcord-web.service > /dev/null <<EOF
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
EOF

print_success "Systemd servisleri oluşturuldu"

# 10. Nginx yapılandırması
print_status "Nginx yapılandırılıyor..."
sudo tee /etc/nginx/sites-available/trendcord > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/trendcord /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
print_success "Nginx yapılandırıldı"

# 11. Firewall ayarları
print_status "Firewall ayarlanıyor..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000
print_success "Firewall ayarlandı"

# 12. Backup scripti oluştur
print_status "Backup scripti oluşturuluyor..."
mkdir -p /home/ubuntu/backups

tee /home/ubuntu/backup.sh > /dev/null <<EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p \$BACKUP_DIR

# Veritabanı backup
if [ -f "/home/ubuntu/trendcord/data/trendyol_tracker.sqlite" ]; then
    cp /home/ubuntu/trendcord/data/trendyol_tracker.sqlite \$BACKUP_DIR/db_backup_\$DATE.sqlite
    echo "Backup completed: \$DATE"
fi

# Eski backupları temizle (30 günden eski)
find \$BACKUP_DIR -name "*.sqlite" -mtime +30 -delete
EOF

chmod +x /home/ubuntu/backup.sh
print_success "Backup scripti oluşturuldu"

# 13. Servisleri etkinleştir
print_status "Servisler etkinleştiriliyor..."
sudo systemctl daemon-reload
sudo systemctl enable trendcord-bot
sudo systemctl enable trendcord-web
sudo systemctl enable nginx
sudo systemctl enable fail2ban

sudo systemctl restart nginx
sudo systemctl start fail2ban
print_success "Servisler etkinleştirildi"

# 14. Yönetim scriptleri oluştur
print_status "Yönetim scriptleri oluşturuluyor..."

# Start script
tee /home/ubuntu/start_trendcord.sh > /dev/null <<EOF
#!/bin/bash
echo "🚀 TrendCord başlatılıyor..."
sudo systemctl start trendcord-bot
sudo systemctl start trendcord-web
echo "✅ TrendCord başlatıldı!"
echo "🌐 Web UI: http://\$(curl -s ifconfig.me):5000"
EOF

# Stop script
tee /home/ubuntu/stop_trendcord.sh > /dev/null <<EOF
#!/bin/bash
echo "🛑 TrendCord durduruluyor..."
sudo systemctl stop trendcord-bot
sudo systemctl stop trendcord-web
echo "✅ TrendCord durduruldu!"
EOF

# Status script
tee /home/ubuntu/status_trendcord.sh > /dev/null <<EOF
#!/bin/bash
echo "📊 TrendCord Durumu:"
echo "==================="
echo "🤖 Discord Bot:"
sudo systemctl status trendcord-bot --no-pager -l
echo ""
echo "🌐 Web UI:"
sudo systemctl status trendcord-web --no-pager -l
echo ""
echo "🔗 Erişim URL'leri:"
echo "Web UI: http://\$(curl -s ifconfig.me):5000"
echo "Nginx: http://\$(curl -s ifconfig.me)"
EOF

# Update script
tee /home/ubuntu/update_trendcord.sh > /dev/null <<EOF
#!/bin/bash
echo "🔄 TrendCord güncelleniyor..."
cd /home/ubuntu/trendcord
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart trendcord-bot
sudo systemctl restart trendcord-web
echo "✅ TrendCord güncellendi!"
EOF

chmod +x /home/ubuntu/*.sh
print_success "Yönetim scriptleri oluşturuldu"

# 15. Kurulum tamamlandı
echo ""
echo "🎉 TrendCord EC2 Kurulumu Tamamlandı!"
echo "====================================="
echo ""
print_success "Kurulum başarıyla tamamlandı!"
echo ""
echo "📋 Sonraki Adımlar:"
echo "1. Discord token'ınızı ekleyin:"
echo "   nano /home/ubuntu/trendcord/.env"
echo ""
echo "2. TrendCord'u başlatın:"
echo "   ./start_trendcord.sh"
echo ""
echo "3. Durumu kontrol edin:"
echo "   ./status_trendcord.sh"
echo ""
echo "🔗 Erişim URL'leri:"
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_PUBLIC_IP")
echo "   Web UI (Doğrudan): http://$PUBLIC_IP:5000"
echo "   Web UI (Nginx): http://$PUBLIC_IP"
echo ""
echo "📚 Yönetim Komutları:"
echo "   ./start_trendcord.sh    - TrendCord'u başlat"
echo "   ./stop_trendcord.sh     - TrendCord'u durdur"
echo "   ./status_trendcord.sh   - Durum kontrolü"
echo "   ./update_trendcord.sh   - Güncelleme"
echo "   ./backup.sh             - Manuel backup"
echo ""
echo "🔧 Servis Komutları:"
echo "   sudo systemctl status trendcord-bot"
echo "   sudo systemctl status trendcord-web"
echo "   sudo journalctl -u trendcord-bot -f"
echo ""
print_warning "ÖNEMLI: .env dosyasını düzenlemeyi unutmayın!"
echo ""