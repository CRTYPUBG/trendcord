#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gerekli bağımlılıkları yükleyen script.
Windows'ta path sorunları yaşayanlar için.
"""

import subprocess
import sys
import os
import logging
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_requirements():
    """requirements_fix.txt dosyasındaki bağımlılıkları yükler."""
    logger.info("Bağımlılıklar yükleniyor...")
    
    try:
        # Bağımlılıkları yükle
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_fix.txt"])
        logger.info("Bağımlılıklar başarıyla yüklendi!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Bağımlılıklar yüklenirken hata oluştu: {e}")
        return False

def check_and_create_env_file():
    """Eğer .env dosyası yoksa örnek bir .env dosyası oluşturur."""
    if not os.path.exists('.env'):
        logger.info(".env dosyası bulunamadı, örnek bir dosya oluşturuluyor...")
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("""# Discord Bot Token - Discord Developer Portal'dan alınacak
DISCORD_TOKEN=buraya_discord_tokeninizi_ekleyin

# Bot Ayarları
PREFIX=!
CHECK_INTERVAL=3600 # Her saatte bir fiyat kontrolü (saniye cinsinden)
PROXY_ENABLED=True # Proxy kullanımını etkinleştir

# Veritabanı Ayarları
DATABASE_PATH=data/trendyol_tracker.db # Ana veritabanı dosyası
BACKUP_DATABASE_PATH=data/database.db # Yedek veritabanı dosyası
""")
        logger.info(".env dosyası oluşturuldu. Lütfen DISCORD_TOKEN değerini ayarlayın.")
        return True
    return False

if __name__ == "__main__":
    logger.info("Trendyol Takip Botu - Kurulum")
    logger.info("--------------------------")
    
    # .env dosyasını kontrol et
    check_and_create_env_file()
    
    # Bağımlılıkları yükle
    if install_requirements():
        # data klasörünü oluştur
        if not os.path.exists('data'):
            os.makedirs('data')
            logger.info("data klasörü oluşturuldu.")
            
        # Veritabanını oluştur
        logger.info("Veritabanı oluşturuluyor...")
        try:
            subprocess.check_call([sys.executable, "init_db.py"])
            logger.info("Veritabanı başarıyla oluşturuldu!")
            
            logger.info("Kurulum tamamlandı!")
            logger.info("Botu başlatmak için 'python main.py' komutunu kullanabilirsiniz.")
            logger.info("NOT: Botu çalıştırmadan önce .env dosyasında DISCORD_TOKEN'ı ayarlamayı unutmayın!")
        except subprocess.CalledProcessError as e:
            logger.error(f"Veritabanı oluşturulurken hata oluştu: {e}")
    
    input("Devam etmek için Enter tuşuna basın...") 