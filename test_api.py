#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trendyol API test scripti
"""

from trendyol_api import TrendyolAPI, TrendyolAPIFallback
from scraper import TrendyolScraper
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api():
    """Trendyol API'sini test eder"""
    print("=== TRENDYOL API TEST ===")
    
    # API client oluştur
    api_client = TrendyolAPI()
    
    # API credentials kontrolü
    if api_client.api_key and api_client.api_secret and api_client.supplier_id:
        print("✅ API credentials bulundu")
        print(f"API Key: {api_client.api_key[:10]}...")
        print(f"Supplier ID: {api_client.supplier_id}")
    else:
        print("⚠️  API credentials bulunamadı, sadece public endpoint'ler test edilecek")
    
    # Test URL'leri
    test_cases = [
        "123456789",  # Basit ID
        "https://www.trendyol.com/test-p-987654321",  # URL format
        "987654321"   # Başka bir ID
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- API Test {i}: {test_case} ---")
        
        # URL doğrulama
        if api_client.is_valid_url(test_case):
            print("✅ URL formatı geçerli")
        else:
            print("❌ URL formatı geçersiz")
            continue
        
        # Ürün ID çıkarma
        product_id = api_client.extract_product_id_from_url(test_case)
        print(f"Çıkarılan Ürün ID: {product_id}")
        
        if not product_id:
            print("❌ Ürün ID'si çıkarılamadı\n")
            continue
        
        # API ile ürün bilgilerini çek
        try:
            print("API ile ürün bilgileri çekiliyor...")
            product_data = api_client.get_product_info(test_case)
            
            if product_data and product_data.get('success'):
                print("✅ API ile başarılı!")
                print(f"  📦 Ad: {product_data.get('name', 'Bulunamadı')}")
                print(f"  💰 Fiyat: {product_data.get('current_price', 'Bulunamadı')} TL")
                print(f"  💸 Orijinal Fiyat: {product_data.get('original_price', 'Bulunamadı')} TL")
                print(f"  🖼️  Resim: {'Var' if product_data.get('image_url') else 'Yok'}")
                print(f"  📊 Kaynak: {product_data.get('source', 'Bilinmiyor')}")
            else:
                print("❌ API ile başarısız")
                if product_data:
                    print(f"  Hata: {product_data.get('error', 'Bilinmeyen hata')}")
                    
        except Exception as e:
            print(f"❌ API test hatası: {e}")

def test_fallback():
    """API + Scraping fallback sistemini test eder"""
    print("\n=== FALLBACK SİSTEMİ TEST ===")
    
    # API client oluştur
    api_client = TrendyolAPI()
    
    # Scraper oluştur
    scraper = TrendyolScraper(use_proxy=False, timeout=15, max_retries=3)
    
    # Fallback sistemi oluştur
    fallback = TrendyolAPIFallback(api_client=api_client, scraper=scraper)
    
    # Test URL'si
    test_url = input("\nTest için bir Trendyol URL'si girin (veya Enter'a basın): ").strip()
    
    if not test_url:
        test_url = "123456789"  # Varsayılan test ID
    
    print(f"\n--- Fallback Test: {test_url} ---")
    
    try:
        print("Fallback sistemi ile test ediliyor...")
        print("(Önce API denenir, başarısız olursa scraping'e geçer)")
        
        result = fallback.get_product_info(test_url)
        
        if result and result.get('success'):
            print("\n✅ BAŞARILI!")
            print(f"  📦 Ad: {result.get('name', 'Bulunamadı')}")
            print(f"  💰 Fiyat: {result.get('current_price', 'Bulunamadı')} TL")
            print(f"  💸 Orijinal Fiyat: {result.get('original_price', 'Bulunamadı')} TL")
            print(f"  🖼️  Resim: {'Var' if result.get('image_url') else 'Yok'}")
            print(f"  📊 Kaynak: {result.get('source', 'Bilinmiyor')}")
            print(f"  🔗 URL: {result.get('url', 'Bulunamadı')}")
        else:
            print("\n❌ BAŞARISIZ!")
            if result:
                print(f"  Hata: {result.get('error', 'Bilinmeyen hata')}")
            
            print("\n💡 Öneriler:")
            print("  1. Gerçek bir Trendyol ürün URL'si deneyin")
            print("  2. API credentials'larınızı kontrol edin")
            print("  3. İnternet bağlantınızı kontrol edin")
            
    except Exception as e:
        print(f"\n❌ Fallback test hatası: {e}")

def test_credentials():
    """API credentials'larını test eder"""
    print("\n=== API CREDENTIALS TEST ===")
    
    api_key = os.getenv('TRENDYOL_API_KEY')
    api_secret = os.getenv('TRENDYOL_API_SECRET')
    supplier_id = os.getenv('TRENDYOL_SUPPLIER_ID')
    
    print(f"API Key: {'✅ Var' if api_key and api_key != 'your_api_key_here' else '❌ Yok'}")
    print(f"API Secret: {'✅ Var' if api_secret and api_secret != 'your_api_secret_here' else '❌ Yok'}")
    print(f"Supplier ID: {'✅ Var' if supplier_id and supplier_id != 'your_supplier_id_here' else '❌ Yok'}")
    
    if api_key and api_key != 'your_api_key_here':
        print(f"API Key preview: {api_key[:10]}...")
    
    if not all([api_key, api_secret, supplier_id]) or any(x in ['your_api_key_here', 'your_api_secret_here', 'your_supplier_id_here'] for x in [api_key, api_secret, supplier_id]):
        print("\n⚠️  API credentials eksik veya varsayılan değerlerde!")
        print("Trendyol Marketplace Partner değilseniz bu normal.")
        print("Bot scraping modunda çalışacak.")
    else:
        print("\n✅ API credentials tamam!")

if __name__ == "__main__":
    test_credentials()
    test_api()
    test_fallback()
    print("\n=== TÜM TESTLER TAMAMLANDI ===")