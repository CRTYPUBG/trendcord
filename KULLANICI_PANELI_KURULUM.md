# Trendyol Bot - Kullanıcı Paneli Kurulum Kılavuzu

## 🔐 Güvenli Kullanıcı Paneli

Bu kılavuz, Discord OAuth ile güvenli giriş yapabilen ve uçtan uca şifrelenmiş kullanıcı panelinin kurulumunu açıklar.

## ✨ Özellikler

- **Discord OAuth Girişi**: Güvenli Discord hesabı ile giriş
- **Uçtan Uca Şifreleme**: Tüm kullanıcı verileri AES-256 ile şifrelenir
- **Kullanıcı İzolasyonu**: Her kullanıcı sadece kendi verilerini görebilir
- **Sunucu Bazlı Erişim**: Kullanıcılar sadece üye oldukları sunucuların verilerine erişebilir
- **Kişisel Ayar Paneli**: Her kullanıcının kendi ayarları
- **Gerçek Zamanlı Bildirimler**: WebSocket ile anlık güncellemeler

## 🛠️ Kurulum

### 1. Gereksinimler

```bash
# Python 3.8+ gerekli
python --version

# Gerekli kütüphaneleri yükle
pip install -r requirements.txt
```

### 2. Discord OAuth Uygulaması Oluşturma

1. [Discord Developer Portal](https://discord.com/developers/applications)'a gidin
2. "New Application" butonuna tıklayın
3. Uygulamanıza bir isim verin (örn: "Trendyol Bot Panel")
4. **OAuth2** sekmesine gidin
5. **Redirects** bölümüne şu URL'yi ekleyin:
   ```
   http://localhost:5001/auth/callback
   ```
6. **Scopes** bölümünden şunları seçin:
   - `identify` (kullanıcı bilgileri için)
   - `guilds` (sunucu listesi için)

### 3. Çevre Değişkenlerini Ayarlama

`.env.example` dosyasını `.env` olarak kopyalayın ve düzenleyin:

```bash
# Discord OAuth Ayarları
DISCORD_CLIENT_ID=your_discord_client_id_here
DISCORD_CLIENT_SECRET=your_discord_client_secret_here
DISCORD_REDIRECT_URI=http://localhost:5001/auth/callback

# Flask Güvenlik Anahtarı
FLASK_SECRET_KEY=your_very_secure_random_key_here

# Global Admin ID'leri (virgülle ayırın)
GLOBAL_ADMIN_IDS=your_discord_user_id_here
```

### 4. Kullanıcı Panelini Başlatma

#### Windows:
```bash
# Batch dosyası ile (önerilen)
start_user_panel.bat

# Veya Python ile
python start_user_panel.py
```

#### Linux/Mac:
```bash
python start_user_panel.py
```

### 5. Erişim

Tarayıcınızda şu adresi açın:
```
http://localhost:5001
```

## 🔒 Güvenlik Özellikleri

### Uçtan Uca Şifreleme
- Tüm kullanıcı verileri AES-256 algoritması ile şifrelenir
- Her kullanıcının kendine özel şifreleme anahtarı vardır
- Şifreleme anahtarları kullanıcı ID'si ve güvenli hash ile türetilir
- Veriler veritabanında şifrelenmiş olarak saklanır

### Kullanıcı İzolasyonu
- Her kullanıcı sadece kendi verilerini görebilir
- Sunucu bazlı erişim kontrolü
- Global adminler tüm verileri görebilir (şifrelenmemiş)
- Oturum tabanlı kimlik doğrulama

### Discord OAuth Güvenliği
- Güvenli Discord OAuth2 akışı
- State parametresi ile CSRF koruması
- Access token'lar güvenli şekilde işlenir
- Oturum süreleri sınırlı (30 gün)

## 👤 Kullanıcı Rolleri

### Normal Kullanıcı
- Kendi ürünlerini yönetebilir
- Üye olduğu sunucuların verilerini görebilir
- Kişisel ayarlarını değiştirebilir
- Fiyat hedefleri oluşturabilir

### Global Admin
- Tüm kullanıcıların verilerini görebilir
- Sistem istatistiklerini görüntüleyebilir
- Admin paneline erişebilir
- Diğer adminleri yönetebilir

## 📱 Kullanım

### 1. Giriş Yapma
1. Ana sayfaya gidin
2. "Discord ile Giriş Yap" butonuna tıklayın
3. Discord hesabınızla yetkilendirin
4. Otomatik olarak dashboard'a yönlendirileceksiniz

### 2. Ürün Ekleme
1. Dashboard'da "Ürün Ekle" butonuna tıklayın
2. Trendyol ürün URL'sini yapıştırın
3. Sunucu seçin (opsiyonel)
4. "Ekle" butonuna tıklayın

### 3. Fiyat Hedefi Oluşturma
1. Ürünlerim sayfasına gidin
2. Ürünün yanındaki hedef butonuna tıklayın
3. Hedef fiyatı ve koşulu belirleyin
4. "Hedef Ekle" butonuna tıklayın

### 4. Ayarları Değiştirme
1. Ayarlar sayfasına gidin
2. Bildirim tercihlerinizi ayarlayın
3. Fiyat kontrol sıklığını belirleyin
4. "Ayarları Kaydet" butonuna tıklayın

## 🔧 Yapılandırma

### Port Değiştirme
```bash
# .env dosyasına ekleyin
USER_PANEL_HOST=0.0.0.0
USER_PANEL_PORT=5001
```

### Debug Modu
```bash
# .env dosyasına ekleyin
DEBUG=true
```

### Veritabanı Yolu
```bash
# .env dosyasına ekleyin
DATABASE_PATH=data/user_panel.sqlite
```

## 🚨 Sorun Giderme

### Discord OAuth Hataları
```
Hata: Discord OAuth yapılandırması eksik
Çözüm: .env dosyasında DISCORD_CLIENT_ID ve DISCORD_CLIENT_SECRET ayarlayın
```

### Şifreleme Hataları
```
Hata: Kullanıcı anahtarı oluşturulamadı
Çözüm: cryptography kütüphanesinin doğru yüklendiğinden emin olun
```

### Veritabanı Hataları
```
Hata: Veritabanı bağlantısı kurulamadı
Çözüm: data/ klasörünün yazılabilir olduğundan emin olun
```

## 📊 Performans

### Önerilen Sistem Gereksinimleri
- **RAM**: Minimum 512MB, Önerilen 1GB
- **CPU**: Herhangi bir modern işlemci
- **Disk**: 100MB boş alan
- **Network**: İnternet bağlantısı

### Optimizasyon İpuçları
- Fiyat kontrol sıklığını ihtiyacınıza göre ayarlayın
- Gereksiz bildirimleri kapatın
- Düzenli olarak eski verileri temizleyin

## 🔄 Güncelleme

```bash
# Git ile güncelleme
git pull origin main

# Gereksinimleri güncelle
pip install -r requirements.txt --upgrade

# Veritabanı migrasyonları (gerekirse)
python migrate_database.py
```

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🆘 Destek

Sorunlarınız için:
1. Bu dokümantasyonu kontrol edin
2. GitHub Issues'da arama yapın
3. Yeni issue oluşturun

## 🔐 Gizlilik

- Hiçbir kişisel veri üçüncü taraflarla paylaşılmaz
- Tüm veriler yerel olarak saklanır
- Discord OAuth sadece kimlik doğrulama için kullanılır
- İstediğiniz zaman verilerinizi silebilirsiniz