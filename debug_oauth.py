#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OAuth Debug Yardımcısı
Discord OAuth ayarlarını test eder
"""

import os
from dotenv import load_dotenv

load_dotenv()

def debug_oauth_settings():
    """OAuth ayarlarını kontrol et"""
    print("=" * 50)
    print("Discord OAuth Debug Bilgileri")
    print("=" * 50)
    
    client_id = os.getenv('DISCORD_CLIENT_ID')
    client_secret = os.getenv('DISCORD_CLIENT_SECRET')
    redirect_uri = os.getenv('DISCORD_REDIRECT_URI')
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {'*' * len(client_secret) if client_secret else 'BOŞ'}")
    print(f"Redirect URI: {redirect_uri}")
    print()
    
    # Kontroller
    if not client_id:
        print("❌ DISCORD_CLIENT_ID eksik!")
    else:
        print("✅ DISCORD_CLIENT_ID mevcut")
    
    if not client_secret:
        print("❌ DISCORD_CLIENT_SECRET eksik!")
    else:
        print("✅ DISCORD_CLIENT_SECRET mevcut")
    
    if not redirect_uri:
        print("❌ DISCORD_REDIRECT_URI eksik!")
    elif redirect_uri != "http://localhost:5001/auth/callback":
        print(f"⚠️  DISCORD_REDIRECT_URI farklı: {redirect_uri}")
        print("   Beklenen: http://localhost:5001/auth/callback")
    else:
        print("✅ DISCORD_REDIRECT_URI doğru")
    
    print()
    print("Discord Developer Portal'da kontrol edilecekler:")
    print("1. https://discord.com/developers/applications")
    print(f"2. Client ID: {client_id} olan uygulamayı bul")
    print("3. OAuth2 → General sekmesine git")
    print("4. Redirects bölümünde şu URL olmalı:")
    print("   http://localhost:5001/auth/callback")
    print()
    
    # Test URL'si oluştur
    if client_id:
        test_url = f"https://discord.com/oauth2/authorize?client_id={client_id}&redirect_uri=http%3A%2F%2Flocalhost%3A5001%2Fauth%2Fcallback&response_type=code&scope=identify%20guilds"
        print("Test URL'si:")
        print(test_url)
        print()
        print("Bu URL'yi tarayıcıda açarak test edebilirsin!")

if __name__ == '__main__':
    debug_oauth_settings()