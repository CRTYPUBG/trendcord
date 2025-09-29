# 🚀 Unified Web App - Kurulum ve Kullanım Kılavuzu

## 📋 Genel Bakış

Unified Web App, tek bir Cloudflare tunnel üzerinden hem admin hem de kullanıcı girişi yapılabilen birleşik web uygulamasıdır.

### ✨ Özellikler

- **👨‍💼 Admin Paneli**: Sistem yöneticileri için tam kontrol
- **👤 Kullanıcı Paneli**: Discord OAuth ile güvenli kullanıcı girişi
- **🌐 Tek Tunnel**: Cloudflare tunnel ile tek URL üzerinden erişim
- **🔒 Güvenli**: Şifrelenmiş kullanıcı verileri ve güvenli oturum yönetimi
- **📱 Responsive**: Mobil ve masaüstü uyumlu arayüz

## 🛠️ Hızlı Kurulum

### 1. Otomatik Kurulum (Önerilen)

```bash
# Hızlı başlatma
.\quick_unified_start.bat
```

### 2. Cloudflare Tunnel Kurulumu

```powershell
# Cloudflare tunnel kurulumu
.\setup_cloudflare_tunnel.ps1 -Domain "yourdomain.com"
```

### 3. Manuel Kurulum

#### Gereksinimler
```bash
pip install flask flask-cors flask-socketio cryptography python-dotenv requests
```

#### .env Dosyası Yapılandırması
```env
# Unified Web App Configuration
WEB_PORT=5000
WEB_HOST=0.0.0.0
CLOUDFLARE_TUNNEL_URL=https://your-domain.com
FLASK_SECRET_KEY=your-super-secret-key

# Admin Configuration
ADMIN_SECRET_KEY=admin123

# Discord OAuth
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=https://your-domain.com/auth/callback
```

## 🌐 Erişim Yolları

### Ana Giriş Sayfası
```
https://your-domain.com/
```

### Admin Girişi
```
https://your-domain.com/login?type=admin
```
- **Kullanıcı Adı**: Admin
- **Şifre**: .env dosyasındaki `ADMIN_SECRET_KEY` değeri

### Kullanıcı Girişi (Discord OAuth)
```
https://your-domain.com/login?type=user
```
- Discord hesabı ile otomatik giriş

## 👨‍💼 Admin Paneli Özellikleri

### Dashboard
- Sistem genel durumu
- Toplam ürün, sunucu ve kullanıcı sayıları
- Bot durumu izleme
- Son eklenen ürünler

### Ürün Yönetimi
- Tüm ürünleri görüntüleme
- Ürün ekleme/silme
- Fiyat güncelleme
- Sunucu bazında filtreleme

### Analitik
- Detaylı istatistikler
- Fiyat trendleri
- En iyi fırsatlar

## 👤 Kullanıcı Paneli Özellikleri

### Dashboard
- Kişisel ürün listesi
- Sunucu bilgileri
- Hızlı ürün ekleme

### Ürün Takibi
- Sadece erişimi olan sunucuların ürünleri
- Ürün ekleme/silme (kendi ürünleri)
- Fiyat bildirimleri

### Bildirimler
- Fiyat hedefleri
- Bildirim geçmişi
- E-posta/Discord bildirimleri

## 🔧 Yapılandırma

### Discord OAuth Kurulumu

1. **Discord Developer Portal**'a gidin: https://discord.com/developers/applications
2. **New Application** butonuna tıklayın
3. Uygulama adını girin (örn: "Trendyol Bot")
4. **OAuth2** sekmesine gidin
5. **Redirects** bölümüne şu URL'yi ekleyin:
   ```
   https://your-domain.com/auth/callback
   ```
6. **Client ID** ve **Client Secret** değerlerini .env dosyasına ekleyin

### Cloudflare Tunnel Yapılandırması

1. **Cloudflare hesabı** oluşturun
2. **Domain** ekleyin ve DNS'i Cloudflare'e yönlendirin
3. Setup scriptini çalıştırın:
   ```powershell
   .\setup_cloudflare_tunnel.ps1 -Domain "yourdomain.com"
   ```

## 🚀 Başlatma

### Otomatik Başlatma
```bash
.\start_unified_app.bat
```

### Manuel Başlatma
```bash
python unified_web_app.py
```

### Cloudflare Tunnel ile Başlatma
```bash
# Terminal 1: Tunnel başlat
cloudflared tunnel run trendyol-bot-unified

# Terminal 2: Web app başlat
python unified_web_app.py
```

## 🛑 Durdurma

```bash
.\stop_unified_app.bat
```

## 📁 Dosya Yapısı

```
trendcord/
├── unified_web_app.py              # Ana uygulama
├── user_auth.py                    # Kullanıcı kimlik doğrulama
├── templates/
│   ├── unified_login.html          # Ana giriş sayfası
│   ├── admin_login.html            # Admin giriş sayfası
│   ├── admin_dashboard.html        # Admin dashboard
│   └── user_dashboard.html         # Kullanıcı dashboard
├── setup_cloudflare_tunnel.ps1    # Cloudflare kurulum scripti
├── quick_unified_start.bat         # Hızlı başlatma
├── start_unified_app.bat           # Otomatik başlatma
└── stop_unified_app.bat            # Durdurma scripti
```

## 🔒 Güvenlik

### Admin Güvenliği
- Admin anahtarı ile korumalı giriş
- Session tabanlı oturum yönetimi
- IP ve User-Agent takibi

### Kullanıcı Güvenliği
- Discord OAuth2 ile güvenli giriş
- Şifrelenmiş kullanıcı verileri
- Sunucu bazında erişim kontrolü
- Oturum süresi sınırlaması

### Veri Güvenliği
- Uçtan uca şifreleme
- Güvenli veritabanı bağlantıları
- HTTPS zorunluluğu

## 🐛 Sorun Giderme

### Port Çakışması
```bash
# Port 5000 kullanımda ise
set WEB_PORT=5001
python unified_web_app.py
```

### Discord OAuth Hatası
1. Redirect URI'yi kontrol edin
2. Client ID/Secret değerlerini doğrulayın
3. Discord uygulaması aktif mi kontrol edin

### Cloudflare Tunnel Hatası
```bash
# Tunnel durumunu kontrol et
cloudflared tunnel list

# Tunnel'i yeniden başlat
cloudflared tunnel run trendyol-bot-unified
```

### Veritabanı Hatası
```bash
# Veritabanını yeniden oluştur
python -c "from database import Database; db = Database(); db.close()"
```

## 📊 API Endpoints

### Genel API'ler
- `GET /api/stats` - Sistem istatistikleri
- `POST /api/add_product` - Ürün ekleme
- `POST /api/delete_product` - Ürün silme

### Admin API'ler
- `GET /api/all_users` - Tüm kullanıcılar
- `POST /api/admin_action` - Admin işlemleri

### User API'ler
- `GET /api/user_products` - Kullanıcı ürünleri
- `POST /api/user_settings` - Kullanıcı ayarları

## 🔄 Güncelleme

```bash
# Git ile güncelleme
git pull origin main

# Bağımlılıkları güncelle
pip install -r requirements.txt

# Veritabanını güncelle
python -c "from database import Database; db = Database(); db.close()"
```

## 📞 Destek

### Loglar
- **Web App**: Console çıktısı
- **Cloudflare**: `~/.cloudflared/` klasörü
- **Database**: `data/` klasörü

### Yaygın Hatalar
1. **Port kullanımda**: Farklı port deneyin
2. **Discord OAuth**: Redirect URI kontrol edin
3. **Tunnel bağlantısı**: Internet bağlantısını kontrol edin
4. **Veritabanı**: Dosya izinlerini kontrol edin

## 🎯 Gelecek Özellikler

- [ ] Multi-language desteği
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] API rate limiting
- [ ] Advanced user roles
- [ ] Webhook integrations

---

## 📝 Notlar

- **Güvenlik**: Admin anahtarını mutlaka değiştirin
- **Backup**: Veritabanını düzenli olarak yedekleyin
- **Monitoring**: Sistem kaynaklarını izleyin
- **Updates**: Düzenli olarak güncellemeleri kontrol edin

**🎉 Unified Web App başarıyla kuruldu! Artık tek URL üzerinden hem admin hem de kullanıcı girişi yapabilirsiniz.**