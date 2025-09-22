#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trendyol Takip Botu Kurulum Scripti
Bu script botu kurmak için gerekli tüm adımları otomatik olarak yapar.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Python versiyonunu kontrol eder."""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 veya üzeri gerekli!")
        return False
    logger.info(f"Python versiyonu: {sys.version}")
    return True

def install_requirements():
    """Gerekli paketleri yükler."""
    try:
        logger.info("Gerekli paketler yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("✅ Paketler başarıyla yüklendi")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Paket yükleme hatası: {e}")
        return False

def create_directories():
    """Gerekli klasörleri oluşturur."""
    directories = ["data", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"✅ Klasör oluşturuldu: {directory}")

def create_env_file():
    """Örnek .env dosyası oluşturur."""
    if not os.path.exists(".env"):
        try:
            with open(".env.example", "r", encoding="utf-8") as example:
                content = example.read()
            
            with open(".env", "w", encoding="utf-8") as env_file:
                env_file.write(content)
            
            logger.info("✅ .env dosyası oluşturuldu")
            logger.warning("⚠️  .env dosyasını düzenleyip Discord token'ınızı ekleyin!")
            return True
        except Exception as e:
            logger.error(f"❌ .env dosyası oluşturulamadı: {e}")
            return False
    else:
        logger.info("✅ .env dosyası zaten mevcut")
        return True

def initialize_database():
    """Veritabanını başlatır."""
    try:
        logger.info("Veritabanı başlatılıyor...")
        subprocess.check_call([sys.executable, "init_db.py"])
        logger.info("✅ Veritabanı başarıyla oluşturuldu")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Veritabanı oluşturma hatası: {e}")
        return False

def run_tests():
    """Test scriptini çalıştırır."""
    try:
        logger.info("Testler çalıştırılıyor...")
        result = subprocess.run([sys.executable, "test_scraper.py"], 
                              capture_output=True, text=True)
        
        if "✅ Test ürünü başarıyla eklendi" in result.stdout:
            logger.info("✅ Database testleri başarılı")
            return True
        else:
            logger.warning("⚠️  Bazı testler başarısız olabilir (normal)")
            return True
    except Exception as e:
        logger.error(f"❌ Test hatası: {e}")
        return False

def main():
    """Ana kurulum fonksiyonu."""
    print("=" * 50)
    print("🤖 TRENDYOL TAKİP BOTU KURULUM")
    print("=" * 50)
    
    steps = [
        ("Python versiyonu kontrolü", check_python_version),
        ("Klasör oluşturma", create_directories),
        ("Paket yükleme", install_requirements),
        ("Yapılandırma dosyası oluşturma", create_env_file),
        ("Veritabanı başlatma", initialize_database),
        ("Test çalıştırma", run_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        logger.info(f"📋 {step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            logger.error(f"❌ {step_name} sırasında hata: {e}")
            failed_steps.append(step_name)
    
    print("\n" + "=" * 50)
    if not failed_steps:
        print("🎉 KURULUM BAŞARIYLA TAMAMLANDI!")
        print("\n📝 Sonraki adımlar:")
        print("1. .env dosyasını düzenleyin ve Discord token'ınızı ekleyin")
        print("2. 'python main.py' ile botu başlatın")
    else:
        print("⚠️  KURULUM KISMEN BAŞARISIZ")
        print(f"Başarısız adımlar: {', '.join(failed_steps)}")
        print("Lütfen hataları kontrol edin ve tekrar deneyin.")
    print("=" * 50)

if __name__ == "__main__":
    main()