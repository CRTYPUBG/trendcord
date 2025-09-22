# 🤖 TrendCord - Gelişmiş Trendyol Fiyat Takip Botu

## 🚀 **Yeni Özellikler v2.0**

### 📊 **Gelişmiş Analitik Sistemi**
- **Fiyat Trend Analizi** - 30 günlük detaylı fiyat trendi
- **En İyi Fırsatlar** - Otomatik fırsat tespiti
- **Akıllı Uyarılar** - %10+ fiyat değişimlerinde otomatik bildirim
- **İnteraktif Grafikler** - Chart.js ile görsel analiz

### 🎯 **Akıllı Bildirim Sistemi**
- **Kişisel Fiyat Hedefleri** - Kullanıcı bazlı hedef belirleme
- **Otomatik Tetikleme** - Hedef fiyata ulaştığında anlık bildirim
- **Bildirim Geçmişi** - Tüm bildirimlerin kaydı
- **Günlük Özetler** - Otomatik günlük raporlar

### 📱 **Mobil Link Desteği**
- ✅ `https://ty.gl/[kod]` formatı destekleniyor
- ✅ `https://tyml.gl/[kod]` formatı destekleniyor
- ✅ Otomatik redirect takibi
- ✅ Gelişmiş URL çözümleme

## 🛠️ **Kurulum**

### 📋 **Gereksinimler**
```bash
pip install -r requirements.txt
```

### ⚙️ **Yapılandırma**
1. `.env.example` dosyasını `.env` olarak kopyalayın
2. Gerekli değişkenleri doldurun:
```env
DISCORD_TOKEN=your_discord_bot_token
FLASK_SECRET_KEY=your_secret_key
GLOBAL_ADMIN_IDS=your_discord_user_id
```

### 🚀 **Başlatma**

#### Discord Bot
```bash
python main.py
```

#### Web Arayüzü
```bash
python start_web_ui.py
```

## 🤖 **Discord Komutları**

### 📦 **Ürün Yönetimi**
```bash
/ekle [url]                    # Ürün ekle
/listele                       # Ürünleri listele
/sil [ürün_id]                # Ürün sil
/kontrol [ürün_id]            # Manuel fiyat kontrolü
```

### 📊 **Analitik Komutları**
```bash
/trend [ürün_id]              # Fiyat trendi analizi
/deals                        # En iyi fırsatlar
/alerts [eşik]                # Fiyat uyarıları
/stats                        # Sunucu istatistikleri
```

### 🎯 **Bildirim Komutları**
```bash
/hedef [ürün] [fiyat] [koşul] # Fiyat hedefi belirle
/hedeflerim                   # Aktif hedeflerim
/hedef-sil [id]               # Hedef kaldır
/bildirimlerim                # Bildirim geçmişi
/ozet                         # Günlük özet
```

## 🌐 **Web Arayüzü**

### 📊 **Ana Özellikler**
- **Dashboard** (`/`) - Genel istatistikler ve özet
- **Ürünler** (`/products`) - Ürün listesi ve yönetimi
- **Analitik** (`/analytics`) - Detaylı analiz ve grafikler
- **Bildirimler** (`/notifications`) - Bildirim yönetimi
- **Ayarlar** (`/settings`) - Bot yapılandırması

### 🎨 **Özellikler**
- **Responsive Tasarım** - Mobil uyumlu
- **Gerçek Zamanlı Güncellemeler** - WebSocket desteği
- **İnteraktif Grafikler** - Chart.js entegrasyonu
- **Modern UI** - DaisyUI + Tailwind CSS

## 📊 **Analitik Özellikleri**

### 📈 **Fiyat Trend Analizi**
- 30 günlük fiyat geçmişi
- Yüzdelik değişim hesaplama
- Ortalama, min, max fiyat analizi
- Görsel trend gösterimi

### 🔥 **Fırsat Tespiti**
- Son 7 günde en çok düşen fiyatlar
- Otomatik indirim hesaplama
- Tasarruf miktarı gösterimi
- Sunucu bazlı filtreleme

### 🚨 **Akıllı Uyarılar**
- Eşik değer sistemi (%10+ değişim)
- Artış/düşüş kategorilendirmesi
- Anlık Discord bildirimleri
- Web push bildirimleri

## 🎯 **Bildirim Sistemi**

### 🎪 **Fiyat Hedefleri**
```bash
# Örnek kullanım
/hedef https://ty.gl/abc123 250 below
# Ürün ₺250'nin altına düştüğünde bildirim al
```

### 📬 **Bildirim Türleri**
- **Fiyat Hedefi** - Belirlenen hedefe ulaşıldığında
- **Fiyat Değişimi** - Normal fiyat değişimlerinde
- **Günlük Özet** - Günlük aktivite raporu
- **Sistem Bildirimleri** - Bot durumu ve hatalar

## 🔧 **Teknik Detaylar**

### 🗄️ **Veritabanı**
- **SQLite** - Hafif ve hızlı
- **Otomatik Backup** - Veri güvenliği
- **Migration Sistemi** - Kolay güncellemeler

### 🌐 **API Entegrasyonu**
- **Trendyol API** - Birincil veri kaynağı
- **Fallback Scraping** - Yedek veri çekme
- **Rate Limiting** - API koruma
- **Proxy Desteği** - IP rotasyonu

### 📊 **Performans**
- **Async İşlemler** - Hızlı veri işleme
- **Cache Sistemi** - Optimize edilmiş sorgular
- **Batch Processing** - Toplu işlemler
- **Memory Management** - Verimli bellek kullanımı

## 🛡️ **Güvenlik**

### 🔐 **Veri Koruma**
- **Encrypted Storage** - Şifreli veri saklama
- **User Isolation** - Kullanıcı bazlı izolasyon
- **Guild Separation** - Sunucu bazlı ayrım
- **Admin Controls** - Yönetici kontrolleri

### 🚫 **Rate Limiting**
- **API Protection** - API koruma
- **User Limits** - Kullanıcı sınırları
- **Spam Prevention** - Spam koruması

## 📱 **Mobil Destek**

### 🔗 **Desteklenen Formatlar**
- ✅ `https://ty.gl/[kod]` - Mobil kısaltılmış linkler
- ✅ `https://tyml.gl/[kod]` - Milla kısaltılmış linkler
- ✅ `https://www.trendyol.com/...` - Normal web linkleri
- ✅ `[sayı]` - Direkt ürün ID'si

### 🔄 **Otomatik İşlemler**
1. **Link Tespiti** - Kısaltılmış link kontrolü
2. **Redirect Takibi** - Gerçek URL bulma
3. **ID Çıkarma** - Ürün ID'si belirleme
4. **Veri Çekme** - Ürün bilgilerini alma

## 🧪 **Test Sistemi**

### ✅ **Test Dosyaları**
```bash
python test_analytics_system.py    # Analitik sistem testi
python test_real_mobile_link.py    # Mobil link testi
python test_scraper.py             # Scraper testi
```

### 📊 **Test Kapsamı**
- ✅ Veritabanı işlemleri
- ✅ API entegrasyonu
- ✅ Scraping sistemi
- ✅ Bildirim sistemi
- ✅ Analitik hesaplamalar

## 🚀 **Deployment**

### 🐳 **Docker Desteği**
```bash
# Docker ile çalıştırma
docker build -t trendcord .
docker run -d --name trendcord -p 5000:5000 trendcord
```

### ☁️ **Cloud Deployment**
- **Heroku** - Kolay deployment
- **Railway** - Modern platform
- **DigitalOcean** - VPS çözümü
- **AWS** - Enterprise çözüm

## 📈 **İstatistikler**

### 📊 **Sistem Metrikleri**
- **Trend Analizi**: ~50ms
- **Fırsat Tespiti**: ~100ms
- **Bildirim Gönderimi**: ~200ms
- **Veritabanı Sorguları**: ~10ms ortalama

### 🎯 **Kullanım İstatistikleri**
- **Desteklenen Formatlar**: 4 farklı link türü
- **Analitik Fonksiyonlar**: 15+ analiz türü
- **Bildirim Türleri**: 6 farklı bildirim
- **Web Sayfaları**: 5 ana sayfa

## 🤝 **Katkıda Bulunma**

### 🔧 **Geliştirme**
1. Repository'yi fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi yapın
4. Test edin
5. Pull request gönderin

### 🐛 **Bug Raporu**
- GitHub Issues kullanın
- Detaylı açıklama yapın
- Log dosyalarını ekleyin
- Repro adımlarını belirtin

## 📞 **Destek**

### 💬 **İletişim**
- **Discord**: Bot sunucumuzda `/yardim`
- **GitHub**: Issues ve Discussions
- **Email**: Proje sahibi ile iletişim

### 📚 **Dokümantasyon**
- **Wiki**: Detaylı kullanım kılavuzu
- **API Docs**: Geliştirici referansı
- **Examples**: Örnek kullanımlar

## 📄 **Lisans**

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 **Teşekkürler**

- **Discord.py** - Bot framework
- **Flask** - Web framework
- **Chart.js** - Grafik kütüphanesi
- **DaisyUI** - UI komponentleri
- **Trendyol** - Veri kaynağı

---

**🎉 TrendCord ile akıllı alışveriş deneyimi!**

*Son güncelleme: 22 Eylül 2025*