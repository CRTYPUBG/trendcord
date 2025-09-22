#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Scraper test scripti - Trendyol ürün çekme işlemlerini test eder
"""

from scraper import TrendyolScraper
from database import Database
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_scraper():
    """Scraper'ı test eder"""
    print("=== TRENDYOL SCRAPER TEST ===")
    
    # Scraper oluştur (proxy olmadan)
    scraper = TrendyolScraper(use_proxy=False, timeout=10)
    
    # Test URL'leri - güncel ürünler
    test_urls = [
        "https://www.trendyol.com/samsung/galaxy-a55-5g-128-gb-samsung-turkiye-garantili-p-773057247",
        "https://www.trendyol.com/xiaomi/redmi-note-13-256-gb-xiaomi-turkiye-garantili-p-740145849",
        "740145849"  # Sadece ID
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- Test {i}: {url} ---")
        
        # URL doğrulama
        if scraper.is_valid_url(url):
            print("✅ URL geçerli")
        else:
            print("❌ URL geçersiz")
            continue
        
        # Ürün ID çıkarma
        product_id = scraper.extract_product_id(url)
        print(f"Ürün ID: {product_id}")
        
        # Ürün bilgilerini çek
        try:
            product_data = scraper.scrape_product(url)
            
            if product_data and product_data.get('success'):
                print("✅ Ürün bilgileri başarıyla çekildi:")
                print(f"  - Ad: {product_data.get('name', 'Bulunamadı')}")
                print(f"  - Fiyat: {product_data.get('current_price', 'Bulunamadı')} TL")
                print(f"  - Orijinal Fiyat: {product_data.get('original_price', 'Bulunamadı')} TL")
                print(f"  - Resim: {'Var' if product_data.get('image_url') else 'Yok'}")
            else:
                print("❌ Ürün bilgileri çekilemedi")
                if product_data:
                    print(f"  Hata: {product_data.get('error', 'Bilinmeyen hata')}")
                    
        except Exception as e:
            print(f"❌ Test sırasında hata: {e}")

def test_database():
    """Database'i test eder"""
    print("\n=== DATABASE TEST ===")
    
    try:
        db = Database()
        
        # Test verisi
        test_product = {
            'product_id': 'test123456',
            'name': 'Test Ürün',
            'url': 'https://www.trendyol.com/test-p-123456',
            'image_url': 'https://test.com/image.jpg',
            'current_price': 99.99,
            'original_price': 129.99,
            'success': True
        }
        
        print("Test ürünü ekleniyor...")
        if db.add_product(test_product, 'test_guild', 'test_user', 'test_channel'):
            print("✅ Test ürünü başarıyla eklendi")
            
            # Ürünü getir
            product = db.get_product('test123456')
            if product:
                print("✅ Ürün başarıyla okundu")
                print(f"  - Ad: {product['name']}")
                print(f"  - Fiyat: {product['current_price']} TL")
            
            # Fiyat güncelle
            if db.update_product_price('test123456', 89.99):
                print("✅ Fiyat başarıyla güncellendi")
            
            # Fiyat geçmişi
            history = db.get_price_history('test123456')
            print(f"✅ Fiyat geçmişi: {len(history)} kayıt")
            
            # Ürünü sil
            if db.delete_product('test123456'):
                print("✅ Test ürünü başarıyla silindi")
        else:
            print("❌ Test ürünü eklenemedi")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Database test hatası: {e}")

if __name__ == "__main__":
    test_scraper()
    test_database()
    print("\n=== TEST TAMAMLANDI ===")