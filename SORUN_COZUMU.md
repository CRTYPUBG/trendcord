# Trendyol Scraper Sorun Çözümü

## Mevcut Sorun
Trendyol'un güçlü anti-bot korumaları nedeniyle ürün bilgileri çekilemiyor. Karşılaştığımız hatalar:

- **403 Forbidden**: Bot trafiği tespit edilip engellenmiş
- **404/410 Gone**: Test URL'leri artık mevcut değil
- **DNS çözümleme hataları**: API endpoint'leri değişmiş olabilir

## Çözüm Önerileri

### 1. Gerçek URL ile Test
Güncel bir Trendyol ürün URL'si ile test yapın:

```bash
# Bot komutunu kullanarak test edin
!ekle https://www.trendyol.com/[GERÇEK_ÜRÜN_URL]
```

### 2. Proxy Kullanımı
`.env` dosyasında proxy'yi etkinleştirin:

```env
PROXY_ENABLED=true
```

Ve `proxies.txt` dosyasına çalışan proxy'ler ekleyin:

```
# proxies.txt
ip:port
ip:port
ip:port
```

### 3. Daha Uzun Timeout
`.env` dosyasında timeout süresini artırın:

```env
TIMEOUT=15
CHECK_INTERVAL=7200  # 2 saat
```

### 4. User-Agent Rotasyonu
Scraper'da farklı User-Agent'lar kullanın (kod içinde zaten mevcut).

## Test Adımları

1. **Gerçek URL ile test**:
   ```bash
   python test_scraper.py
   ```

2. **Bot ile test**:
   ```bash
   python main.py
   # Discord'da: !ekle [URL]
   ```

3. **Database test**:
   ```bash
   python -c "from database import Database; db = Database(); print('DB OK' if db.test_database() else 'DB FAIL')"
   ```

## Alternatif Çözümler

### Manuel Fiyat Girişi
Eğer scraping çalışmıyorsa, manuel fiyat girişi özelliği eklenebilir:

```python
# Yeni komut önerisi
!manuel_ekle "Ürün Adı" 299.99 "https://trendyol.com/..."
```

### Webhook Entegrasyonu
Trendyol'un resmi API'si veya webhook'ları varsa bunları kullanın.

### Scheduled Jobs
Fiyat kontrollerini daha seyrek yapın (günde 1-2 kez).

## Hata Ayıklama

### Log Kontrolü
```bash
tail -f logs/bot.log
```

### Network Testi
```bash
curl -H "User-Agent: Mozilla/5.0..." "https://www.trendyol.com/test-url"
```

### Proxy Testi
```bash
curl --proxy ip:port "https://www.trendyol.com"
```

## Önerilen Ayarlar

`.env` dosyası:
```env
DISCORD_TOKEN=your_token_here
PREFIX=!
CHECK_INTERVAL=7200
PROXY_ENABLED=true
VERIFY_SSL=false
DATABASE_PATH=data/trendyol_tracker.sqlite
TIMEOUT=15
MAX_RETRIES=5
```

## Sonuç

Trendyol'un anti-bot korumaları nedeniyle scraping zorlaşmıştır. En iyi çözüm:

1. **Gerçek URL'lerle test yapın**
2. **Proxy kullanın**
3. **Daha uzun aralıklarla kontrol edin**
4. **Manuel backup sistemi ekleyin**

Bu adımları takip ederek sistemi çalışır hale getirebilirsiniz.