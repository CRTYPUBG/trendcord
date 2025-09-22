#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Yeni gelişmiş scraper test scripti
"""

from scraper import TrendyolScraper
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_new_scraper():
    """Yeni gelişmiş scraper'ı test eder"""
    print("=== YENİ GELİŞMİŞ SCRAPER TEST ===")
    
    # Scraper oluştur
    scraper = TrendyolScraper(use_proxy=False, verify_ssl=True)
    
    print("✅ Yeni scraper başarıyla oluşturuldu")
    print("🔧 Özellikler:")
    print("  - Gelişmiş retry mekanizması")
    print("  - Çoklu fiyat çıkarma yöntemi")
    print("  - JSON-LD desteği")
    print("  - JavaScript değişken parsing")
    print("  - Stok durumu kontrolü")
    print("  - Gelişmiş hata yönetimi")
    
    # Test URL'si al
    test_url = input("\nTest için bir Trendyol URL'si girin (veya Enter'a basın): ").strip()
    
    if not test_url:
        print("Varsayılan test ID'si kullanılıyor...")
        test_url = "123456789"
    
    print(f"\n--- Test: {test_url} ---")
    
    # URL doğrulama
    if scraper.is_valid_url(test_url):
        print("✅ URL formatı geçerli")
    else:
        print("❌ URL formatı geçersiz")
        return
    
    # Ürün ID çıkarma
    product_id = scraper.extract_product_id(test_url)
    print(f"Çıkarılan Ürün ID: {product_id}")
    
    if not product_id:
        print("❌ Ürün ID'si çıkarılamadı")
        return
    
    # Ürün bilgilerini çek
    try:
        print("\n🔄 Ürün bilgileri çekiliyor...")
        print("(Bu işlem 30-60 saniye sürebilir)")
        
        product_data = scraper.scrape_product(test_url)
        
        if product_data and product_data.get('success'):
            print("\n✅ BAŞARILI! Ürün bilgileri çekildi:")
            print(f"  📦 Ad: {product_data.get('name', 'Bulunamadı')}")
            print(f"  💰 Fiyat: {product_data.get('current_price', 'Bulunamadı')} TL")
            print(f"  💸 Orijinal Fiyat: {product_data.get('original_price', 'Bulunamadı')} TL")
            print(f"  🖼️  Resim: {'Var' if product_data.get('image_url') else 'Yok'}")
            print(f"  🔗 URL: {product_data.get('url', 'Bulunamadı')}")
            
            # İndirim hesapla
            current = product_data.get('current_price')
            original = product_data.get('original_price')
            if current and original and original > current:
                discount = ((original - current) / original) * 100
                print(f"  🎯 İndirim: %{discount:.1f}")
            
            print("\n🎉 Bu URL ile bot komutunu kullanabilirsiniz!")
            print(f"Discord'da: !ekle {test_url}")
            
        else:
            print("\n❌ BAŞARISIZ! Ürün bilgileri çekilemedi")
            if product_data:
                print(f"  Hata: {product_data.get('error', 'Bilinmeyen hata')}")
            
            print("\n🔧 Yeni scraper özellikleri:")
            print("  ✅ Çoklu retry mekanizması")
            print("  ✅ Gelişmiş fiyat parsing")
            print("  ✅ JSON-LD desteği")
            print("  ✅ Stok durumu kontrolü")
            print("  ✅ Anti-bot koruması aşma")
            
            print("\n💡 Öneriler:")
            print("  1. Gerçek ve güncel bir Trendyol ürün URL'si deneyin")
            print("  2. Ürünün stokta olduğunu kontrol edin")
            print("  3. Daha sonra tekrar deneyin")
            print("  4. Manuel ekleme kullanın: !manuel_ekle")
                    
    except Exception as e:
        print(f"\n❌ Test sırasında hata: {e}")

def compare_scrapers():
    """Eski ve yeni scraper'ları karşılaştırır"""
    print("\n=== SCRAPER KARŞILAŞTIRMASI ===")
    
    print("🔄 ESKİ SCRAPER:")
    print("  - Basit HTML parsing")
    print("  - Sınırlı CSS seçiciler")
    print("  - Proxy desteği")
    print("  - Temel retry mekanizması")
    
    print("\n🚀 YENİ SCRAPER:")
    print("  - Gelişmiş HTML parsing")
    print("  - Çoklu extraction yöntemi")
    print("  - JSON-LD desteği")
    print("  - JavaScript değişken parsing")
    print("  - Stok durumu kontrolü")
    print("  - Gelişmiş retry stratejisi")
    print("  - HTTP adapter ile connection pooling")
    print("  - Daha iyi hata yönetimi")
    
    print("\n📊 AVANTAJLAR:")
    print("  ✅ Daha yüksek başarı oranı")
    print("  ✅ Daha güvenilir fiyat çıkarma")
    print("  ✅ Stok durumu tespiti")
    print("  ✅ Daha az hata")
    print("  ✅ Daha hızlı işlem")

if __name__ == "__main__":
    compare_scrapers()
    test_new_scraper()
    print("\n=== YENİ SCRAPER TEST TAMAMLANDI ===")