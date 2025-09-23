# Cloudflare Tunnel Kurulumu - Kullanıcı Paneli

## 🌐 Mevcut Tunnel'ı Kullanıcı Paneli için Ayarla

### 1. Cloudflare Tunnel Config
Eğer zaten bir tunnel'ın varsa, config dosyasını güncelle:

```yaml
# cloudflared config.yml
tunnel: your-tunnel-id
credentials-file: /path/to/credentials.json

ingress:
  # Ana bot web arayüzü (mevcut)
  - hostname: vocabulary-wolf-bin-writes.trycloudflare.com
    service: http://localhost:5000
    path: /
  
  # Kullanıcı paneli (yeni)
  - hostname: vocabulary-wolf-bin-writes.trycloudflare.com
    service: http://localhost:3000
    path: /user/*
  
  # Fallback
  - service: http_status:404
```

### 2. Alternatif - Ayrı Subdomain
Daha iyi bir çözüm için ayrı subdomain kullan:

```yaml
ingress:
  # Ana bot
  - hostname: bot.vocabulary-wolf-bin-writes.trycloudflare.com
    service: http://localhost:5000
  
  # Kullanıcı paneli
  - hostname: panel.vocabulary-wolf-bin-writes.trycloudflare.com
    service: http://localhost:3000
  
  - service: http_status:404
```

### 3. Basit Çözüm - Port Yönlendirme
En basit çözüm, kullanıcı panelini farklı bir port'ta çalıştır:

```bash
# Ana bot: localhost:5000 -> cloudflare
# Kullanıcı paneli: localhost:3000 -> manuel tunnel
cloudflared tunnel --url http://localhost:3000
```

## 🔧 Hızlı Test

1. Kullanıcı panelini başlat: `python start_user_panel.py`
2. Yeni terminal aç ve tunnel başlat: `cloudflared tunnel --url http://localhost:3000`
3. Yeni URL'yi Discord OAuth'da güncelle