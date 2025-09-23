@echo off
title Discord OAuth Kurulum Yardimcisi

echo ================================================
echo Discord OAuth Kurulum Yardimcisi
echo ================================================
echo.

echo 1. Discord Developer Portal'a gidin:
echo    https://discord.com/developers/applications
echo.
echo 2. "New Application" butonuna tiklayin
echo.
echo 3. OAuth2 ayarlarini yapin:
echo    - General sekmesinden Client ID ve Client Secret alin
echo    - Redirects bolumune ekleyin: http://localhost:5001/auth/callback
echo.
echo 4. Asagidaki bilgileri hazirlayin:
echo    - Discord Client ID
echo    - Discord Client Secret  
echo    - Discord User ID (kendi ID'niz)
echo.

pause

echo .env dosyasi olusturuluyor...

REM .env.template'i .env olarak kopyala
if exist ".env.template" (
    copy ".env.template" ".env"
    echo .env dosyasi olusturuldu!
    echo.
    echo ONEMLI: .env dosyasini duzenleyin ve asagidaki degerleri doldurun:
    echo - DISCORD_CLIENT_ID
    echo - DISCORD_CLIENT_SECRET
    echo - GLOBAL_ADMIN_IDS
    echo.
) else (
    echo HATA: .env.template dosyasi bulunamadi!
)

echo Kurulum tamamlandiktan sonra kullanici panelini baslatmak icin:
echo start_user_panel.bat
echo.

pause