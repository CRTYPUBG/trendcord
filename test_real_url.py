#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gerçek URL ile test scripti
Kullanıcıdan URL alır ve test eder
"""

from scraper import TrendyolScraper
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_real_url():
    """Kullanıcıdan URL alarak gerçek test yapar"""
    print("=== GERÇEK URL İLE TEST ===")
    print("Lütfen test etmek istediğiniz Trendyol ürün URL'sini girin.")
    print("Örnek: https://www.trendyol.com/marka/urun-adi-p-123456789")
    print("Veya sadece ürün ID'si: 123456789")
    print("Çıkmak için 'q' yazın.\n")
    
    # Scraper oluştur
    scraper = TrendyolScraper(use_proxy=False, timeout=15, max_retries=5)
    
    while True:
        try:
            url = input("URL veya ID girin: ").strip()
            
            if url.lower() in ['q', 'quit', 'exit', 'çık']:
                print("Test sonlandırılıyor...")
                break
            
            if not url:
                print("❌ Lütfen geçerli bir URL veya ID girin.\n")
                continue
            
            print(f"\n--- Test ediliyor: {url} ---")
            
            # URL doğrulama
            if scraper.is_valid_url(url):
                print("✅ URL formatı geçerli")
            else:
                print("❌ URL formatı geçersiz")
                continue
            
            # Ürün ID çıkarma
            product_id = scraper.extract_product_id(url)
            print(f"Çıkarılan Ürün ID: {product_id}")
            
            if not product_id:
                print("❌ Ürün ID'si çıkarılamadı\n")
                continue
            
            # Ürün bilgilerini çek
            print("Ürün bilgileri çekiliyor... (Bu işlem 30 saniye kadar sürebilir)")
            product_data = scraper.scrape_product(url)
            
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
                print(f"Discord'da: !ekle {url}")
                
            else:
                print("\n❌ BAŞARISIZ! Ürün bilgileri çekilemedi")
                if product_data:
                    print(f"  Hata: {product_data.get('error', 'Bilinmeyen hata')}")
                
                print("\n🔧 Öneriler:")
                print("  1. URL'nin doğru ve güncel olduğundan emin olun")
                print("  2. Ürünün stokta olduğunu kontrol edin")
                print("  3. Proxy kullanmayı deneyin (PROXY_ENABLED=true)")
                print("  4. Daha sonra tekrar deneyin")
            
            print("\n" + "="*50 + "\n")
                    
        except KeyboardInterrupt:
            print("\n\nTest kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            print(f"\n❌ Test sırasında hata: {e}")
            print("Lütfen tekrar deneyin.\n")

if __name__ == "__main__":
    test_real_url()