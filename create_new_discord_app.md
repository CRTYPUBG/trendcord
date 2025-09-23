# Yeni Discord Uygulaması Oluşturma

## Adım 1: Yeni Uygulama Oluştur
1. https://discord.com/developers/applications
2. "New Application" butonuna tıkla
3. İsim: "Trendyol Bot Panel v2"
4. "Create" butonuna tıkla

## Adım 2: OAuth2 Ayarları
1. Sol menüden "OAuth2" sekmesine git
2. "General" alt sekmesine git
3. Client ID'yi kopyala
4. "Reset Secret" butonuna tıkla ve Client Secret'ı kopyala

## Adım 3: Redirect URI Ekle
1. "Redirects" bölümüne şu URL'yi ekle:
   ```
   http://localhost:3000/auth/callback
   ```
2. "Save Changes" butonuna tıkla

## Adım 4: .env Dosyasını Güncelle
```bash
DISCORD_CLIENT_ID=YENİ_CLIENT_ID_BURAYA
DISCORD_CLIENT_SECRET=YENİ_CLIENT_SECRET_BURAYA
DISCORD_REDIRECT_URI=http://localhost:3000/auth/callback
```

## Adım 5: Test Et
```bash
python start_user_panel.py
```

Tarayıcıda: http://localhost:3000