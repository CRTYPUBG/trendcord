#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Alternatif Scraper test scripti
"""

from scraper_alt import TrendyolScraperAlt
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_alt_scraper():
    """Alternatif scraper'ı test eder"""
    print("=== ALTERNATIF TRENDYOL SCRAPER TEST ===")
    
    # Scraper oluştur
    scraper = TrendyolScraperAlt(use_proxy=False, timeout=15)
    
    # Test URL'leri - daha basit ID'ler
    test_cases = [
        "123456789",  # Basit ID
        "987654321",  # Başka bir ID
        "https://www.trendyol.com/test-p-123456789"  # URL format
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case} ---")
        
        # URL doğrulama
        if scraper.is_valid_url(test_case):
            print("✅ URL geçerli")
        else:
            print("❌ URL geçersiz")
            continue
        
        # Ürün ID çıkarma
        product_id = scraper.extract_product_id(test_case)
        print(f"Ürün ID: {product_id}")
        
        # Ürün bilgilerini çek
        try:
            product_data = scraper.scrape_product(test_case)
            
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

if __name__ == "__main__":
    test_alt_scraper()
    print("\n=== ALTERNATİF TEST TAMAMLANDI ===")