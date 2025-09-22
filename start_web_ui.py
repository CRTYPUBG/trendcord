#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trendyol Bot Web UI Launcher
Web arayüzünü başlatmak için kullanılır
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_requirements():
    """Gerekli paketlerin yüklü olup olmadığını kontrol eder"""
    required_packages = [
        'flask',
        'flask_cors', 
        'flask_socketio',
        'requests',
        'bs4',  # beautifulsoup4 import name
        'dotenv'  # python-dotenv import name
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error("Eksik paketler tespit edildi:")
        for package in missing_packages:
            logger.error(f"  - {package}")
        logger.error("Eksik paketleri yüklemek için: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Ortam değişkenlerini kontrol eder"""
    logger.info("Ortam değişkenleri kontrol ediliyor...")
    
    # Opsiyonel ayarlar
    optional_vars = {
        'FLASK_SECRET_KEY': 'Flask güvenlik anahtarı',
        'DISCORD_TOKEN': 'Discord bot token',
        'GLOBAL_ADMIN_IDS': 'Global admin ID\'leri'
    }
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: {'*' * min(len(value), 10)}...")
        else:
            logger.warning(f"⚠️  {var}: Tanımlı değil ({description})")
    
    return True

def start_web_ui(host='0.0.0.0', port=5000, debug=False):
    """Web UI'yi başlatır"""
    try:
        logger.info("Web UI başlatılıyor...")
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        logger.info(f"Debug: {debug}")
        
        # Web UI modülünü import et
        from web_ui import run_web_ui
        
        # Web UI'yi başlat
        success = run_web_ui(host=host, port=port, debug=debug)
        
        if not success:
            logger.error("Web UI başlatılamadı!")
            return False
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Web UI kullanıcı tarafından durduruldu")
        return True
    except Exception as e:
        logger.error(f"Web UI başlatılırken hata: {e}")
        return False

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='Trendyol Bot Web UI Launcher')
    parser.add_argument('--host', default='0.0.0.0', help='Host adresi (varsayılan: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port numarası (varsayılan: 5000)')
    parser.add_argument('--debug', action='store_true', help='Debug modunu etkinleştir')
    parser.add_argument('--no-check', action='store_true', help='Ön kontrolleri atla')
    
    args = parser.parse_args()
    
    print("🤖 Trendyol Bot Web UI Launcher")
    print("=" * 50)
    
    if not args.no_check:
        # Gereksinimler kontrolü
        logger.info("Gereksinimler kontrol ediliyor...")
        if not check_requirements():
            logger.error("Gereksinimler karşılanmıyor!")
            return 1
        
        # Ortam kontrolü
        if not check_environment():
            logger.error("Ortam ayarları eksik!")
            return 1
        
        logger.info("✅ Tüm kontroller başarılı!")
    
    # Web UI'yi başlat
    success = start_web_ui(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    if success:
        logger.info("Web UI başarıyla tamamlandı")
        return 0
    else:
        logger.error("Web UI başlatılamadı")
        return 1

if __name__ == '__main__':
    sys.exit(main())