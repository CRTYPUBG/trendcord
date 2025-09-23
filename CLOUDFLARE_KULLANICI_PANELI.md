# Cloudflare Tunnel ile Kullanıcı Paneli Erişimi

## 🌐 Mevcut Cloudflare URL'si
```
https://vocabulary-wolf-bin-writes.trycloudflare.com
```

## 🔧 Kullanıcı Paneli Kurulumu

### 1. Discord OAuth Ayarları
Discord Developer Portal'da redirect URI'yi güncelle:
```
https://vocabulary-wolf-bin-writes.trycloudflare.com/auth/callback
```

### 2. .env Dosyası Ayarları
```bash
DISCORD_REDIRECT_URI=https://vocabulary-wolf-bin-writes.trycloudflare.com/auth/callback
USER_PANEL_PORT=3000
```

### 3. Servisleri Başlat
```powershell
# Tüm servisleri başlat (önerilen)
.\start_all.ps1

# Veya manuel olarak
.\update_server.ps1

# Veya sadece yeniden başlat
.\restart_services.ps1
```

## 🎯 Erişim URL'leri

### Ana Panel (Admin)
- **Yerel:** http://localhost:5000
- **Cloudflare:** https://vocabulary-wolf-bin-writes.trycloudflare.com

### Kullanıcı Paneli (Discord OAuth)
- **Yerel:** http://localhost:3000
- **Cloudflare:** Ayrı tunnel gerekli veya proxy ayarı

## 🔄 Cloudflare Tunnel Ayarları (Otomatik Çift Tunnel)

### Otomatik Çift Tunnel (Varsayılan)
Update scriptleri otomatik olarak her panel için ayrı tunnel başlatır:
- **Ana Panel:** Port 5000 için tunnel
- **Kullanıcı Paneli:** Port 3000 için tunnel

```powershell
# Otomatik çift tunnel başlat
.\update_server.ps1
# veya
.\start_all.ps1
```

### Tunnel URL'lerini Yakala
```powershell
# URL'leri otomatik yakala
.\get_tunnel_urls.ps1

# Watch modunda sürekli izle
.\get_tunnel_urls.ps1 -Watch
```

### Seçenek 3: Nginx Proxy (Gelişmiş)
Tek tunnel ile her iki paneli serve et:
```nginx
server {
    listen 8080;
    
    location / {
        proxy_pass http://localhost:5000;
    }
    
    location /user {
        proxy_pass http://localhost:3000/;
    }
}
```

## 🚀 Hızlı Başlangıç

1. **Servisleri başlat:**
   ```powershell
   .\start_all.ps1
   ```

2. **Discord OAuth'u test et:**
   ```
   https://discord.com/oauth2/authorize?client_id=1420101853663723684&redirect_uri=https%3A%2F%2Fvocabulary-wolf-bin-writes.trycloudflare.com%2Fauth%2Fcallback&response_type=code&scope=identify%20guilds
   ```

3. **Kullanıcı paneline eriş:**
   ```
   https://vocabulary-wolf-bin-writes.trycloudflare.com
   ```

## 🔍 Sorun Giderme

### OAuth Hatası
```
Geçersiz OAuth2 redirect_url
```
**Çözüm:** Discord Developer Portal'da redirect URI'yi kontrol et

### Port Çakışması
```
Port 3000 already in use
```
**Çözüm:** Mevcut servisleri durdur:
```powershell
.\stop_all.ps1
.\start_all.ps1
```

### Tunnel Bağlantı Hatası
```
Cloudflare tunnel not accessible
```
**Çözüm:** Tunnel'ı yeniden başlat:
```powershell
# Cloudflared'i durdur
taskkill /f /im cloudflared.exe

# Yeniden başlat
cloudflared tunnel --url http://localhost:5000
```

## 📊 Servis Durumu Kontrolü

```powershell
# Çalışan servisleri kontrol et
Get-Process -Name "python" | Where-Object { $_.CommandLine -like "*start_*" }
Get-Process -Name "cloudflared"

# Port durumunu kontrol et
netstat -an | Select-String ":5000\|:3000"
```

## 🎨 Kullanıcı Paneli Özellikleri

- ✅ Discord OAuth2 ile güvenli giriş
- ✅ Uçtan uca şifreleme
- ✅ Kişisel ürün yönetimi
- ✅ Sunucu bazlı erişim kontrolü
- ✅ Fiyat hedefleri ve bildirimler
- ✅ Modern responsive tasarım

## 📝 Notlar

- Ana panel (Port 5000): Admin işlemleri
- Kullanıcı paneli (Port 3000): Discord OAuth girişi
- Cloudflare tunnel: Dış erişim için
- .env dosyası: Hassas bilgiler (commit edilmez)