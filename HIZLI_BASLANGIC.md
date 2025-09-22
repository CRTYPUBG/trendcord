# 🚀 Hızlı Başlangıç Kılavuzu

Bu kılavuz, Trendyol Takip Botu'nu hızlıca kurup çalıştırmanız için hazırlanmıştır.

## ⚡ Otomatik Kurulum (Önerilen)

```bash
# 1. Kurulum scriptini çalıştır
python setup.py

# 2. .env dosyasını düzenle (Discord token ekle)
# 3. Botu başlat
python main.py
```

## 🔧 Manuel Kurulum

### 1. Gereksinimler
- Python 3.8+
- Discord Bot Token

### 2. Kurulum Adımları

```bash
# Paketleri yükle
pip install -r requirements.txt

# Veritabanını oluştur
python init_db.py

# .env dosyasını oluştur
copy .env.example .env
```

### 3. Yapılandırma

`.env` dosyasını düzenleyin:
```env
DISCORD_TOKEN=your_discord_bot_token_here
PREFIX=!
CHECK_INTERVAL=3600
PROXY_ENABLED=False
```

### 4. Botu Başlat

```bash
python main.py
```

## 🧪 Test

```bash
# Sistemi test et
python test_scraper.py
```

## 📋 Komutlar

### Prefix Komutları (!)
- `!ekle <URL>` - Ürün takibe al
- `!takiptekiler` - Takip edilen ürünleri listele
- `!bilgi <ID/URL>` - Ürün detayları
- `!sil <ID>` - Ürünü takipten çıkar
- `!güncelle <ID>` - Ürünü manuel güncelle
- `!yardım` - Yardım menüsü

### Slash Komutları (/)
- `/ekle` - Ürün takibe al
- `/takiptekiler` - Takip edilen ürünleri listele
- `/bilgi` - Ürün detayları
- `/sil` - Ürünü takipten çıkar
- `/guncelle` - Ürünü manuel güncelle
- `/yardim` - Yardım menüsü

## 🔧 Sorun Giderme

### Bot çalışmıyor
- Discord token'ı doğru mu?
- Bot sunucuya davet edildi mi?
- Gerekli izinler verildi mi?

### Ürün bilgileri çekilmiyor
- İnternet bağlantısı var mı?
- Trendyol URL'si doğru mu?
- Proxy ayarları kontrol edin

### Veritabanı hatası
- `data` klasörü var mı?
- Yazma izni var mı?
- `python init_db.py` çalıştırın

## 📞 Destek

Sorun yaşıyorsanız:
1. `test_scraper.py` çalıştırın
2. Log dosyalarını kontrol edin
3. GitHub Issues'da sorun bildirin

## 🎯 İpuçları

- Fiyat kontrol aralığını çok düşük yapmayın (min 1800 saniye)
- Proxy kullanımı opsiyoneldir
- Düzenli olarak veritabanını yedekleyin
- Bot'u 7/24 çalıştırmak için VPS kullanın