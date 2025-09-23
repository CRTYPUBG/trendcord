#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kullanıcı Paneli Debug Scripti
Port ve bağlantı sorunlarını tespit eder
"""

import socket
import sys
import os
from dotenv import load_dotenv

def check_port(host, port):
    """Port'un açık olup olmadığını kontrol et"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Port kontrolü hatası: {e}")
        return False

def check_requirements():
    """Gerekli kütüphaneleri kontrol et"""
    required = ['flask', 'flask_cors', 'flask_socketio', 'cryptography', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def main():
    print("=" * 50)
    print("Kullanıcı Paneli Debug")
    print("=" * 50)
    
    # .env dosyası kontrolü
    if os.path.exists('.env'):
        print("✅ .env dosyası mevcut")
        load_dotenv()
        
        # Gerekli değişkenleri kontrol et
        required_vars = ['DISCORD_CLIENT_ID', 'DISCORD_CLIENT_SECRET', 'FLASK_SECRET_KEY']
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"❌ {var}: Eksik!")
    else:
        print("❌ .env dosyası bulunamadı!")
    
    print()
    
    # Kütüphane kontrolü
    missing = check_requirements()
    if missing:
        print(f"❌ Eksik kütüphaneler: {', '.join(missing)}")
        print("Çözüm: pip install -r requirements.txt")
    else:
        print("✅ Tüm kütüphaneler mevcut")
    
    print()
    
    # Port kontrolü
    ports_to_check = [3000, 5000, 80, 443]
    for port in ports_to_check:
        if check_port('localhost', port):
            print(f"⚠️  Port {port}: Kullanımda")
        else:
            print(f"✅ Port {port}: Boş")
    
    print()
    
    # Flask test
    try:
        from flask import Flask
        test_app = Flask(__name__)
        
        @test_app.route('/')
        def test():
            return "Test OK"
        
        print("✅ Flask test başarılı")
        
        # Test sunucusu başlat
        print("🧪 Test sunucusu başlatılıyor (Port 3001)...")
        test_app.run(host='127.0.0.1', port=3001, debug=False, use_reloader=False)
        
    except Exception as e:
        print(f"❌ Flask test hatası: {e}")
    
    print()
    print("Debug tamamlandı!")

if __name__ == '__main__':
    main()