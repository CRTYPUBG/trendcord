#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kullanıcı Paneli Başlatma Scripti
Discord OAuth ile güvenli kullanıcı panelini başlatır
"""

import os
import sys
import logging
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Logs klasörünü oluştur
os.makedirs('logs', exist_ok=True)

# Logging ayarları (UTF-8 encoding ile)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/user_panel.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_requirements():
    """Gerekli kütüphaneleri kontrol et"""
    required_packages = [
        'flask',
        'flask_cors',
        'flask_socketio',
        'cryptography',
        'requests',
        'sqlite3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.error("Please run 'pip install -r requirements.txt'")
        return False
    
    return True

def check_environment():
    """Çevre değişkenlerini kontrol et"""
    required_env_vars = [
        'DISCORD_CLIENT_ID',
        'DISCORD_CLIENT_SECRET',
        'FLASK_SECRET_KEY'
    ]
    
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Eksik çevre değişkenleri: {', '.join(missing_vars)}")
        logger.error("Lütfen .env dosyanızı kontrol edin")
        return False
    
    return True

def create_directories():
    """Gerekli klasörleri oluştur"""
    directories = [
        'data',
        'logs'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Directory created/checked: {directory}")
        except Exception as e:
            logger.error(f"Klasör oluşturma hatası ({directory}): {e}")
            return False
    
    return True

def main():
    """Ana fonksiyon"""
    logger.info("=" * 50)
    logger.info("Trendyol Bot - User Panel Starting")
    logger.info("=" * 50)
    
    # Gereksinimler kontrolü
    logger.info("Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    
    # Çevre değişkenleri kontrolü
    logger.info("Checking environment variables...")
    if not check_environment():
        sys.exit(1)
    
    # Klasörler oluştur
    logger.info("Creating directories...")
    if not create_directories():
        sys.exit(1)
    
    # Kullanıcı panelini başlat
    try:
        from user_web_ui import run_user_web_ui
        
        host = os.getenv('USER_PANEL_HOST', '0.0.0.0')
        port = int(os.getenv('USER_PANEL_PORT', '5001'))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"Kullanıcı paneli başlatılıyor: http://{host}:{port}")
        logger.info("Güvenli giriş için Discord OAuth kullanılıyor")
        logger.info("Tüm kullanıcı verileri uçtan uca şifreleniyor")
        
        if debug:
            logger.warning("DEBUG modu aktif - Üretim ortamında kapatın!")
        
        # Kullanıcı panelini başlat
        run_user_web_ui(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        logger.info("Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"User panel startup error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()