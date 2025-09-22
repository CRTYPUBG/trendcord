#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gerçek mobil link test scripti
"""

from scraper import TrendyolScraper
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_real_mobile_link():
    """Gerçek mobil linki test eder"""
    print("=== GERÇEK MOBİL LİNK TEST ===")
    
    # Scraper oluştur
    scraper = TrendyolScraper(use_proxy=False, verify_ssl=True)
    
    # Kullanıcının verdiği gerçek link
    test_link = "https://ty.gl/reii1wcijhbf1"
    
    print(f"🔗 Test Link: {test_link}")
    
    # URL doğrulama
    if scraper.is_valid_url(test_link):
        print("✅ URL formatı geçerli")
    else:
        print("❌ URL formatı geçersiz")
        return False
    
    try:
        # Redirect test
        print("\n1️⃣ Redirect Test...")
        full_url = scraper._get_full_url(test_link)
        print(f"Tam URL: {full_url}")
        
        if full_url != test_link:
            print("✅ Redirect başarılı!")
        else:
            print("⚠️ Redirect yapılmadı")
        
        # Ürün ID çıkarma
        print("\n2️⃣ Ürün ID Çıkarma...")
        product_id = scraper.extract_product_id(test_link)
        print(f"Ürün ID: {product_id}")
        
        if product_id:
            print("✅ Ürün ID başarıyla çıkarıldı!")
        else:
            print("❌ Ürün ID çıkarılamadı")
            return False
        
        # Scraping test (gerçek)
        print("\n3️⃣ Scraping Test...")
        print("⚠️ Bu işlem 30-60 saniye sürebilir...")
        
        product_data = scraper.scrape_product(test_link)
        
        if product_data and product_data.get('success'):
            print("\n🎉 BAŞARILI! Mobil link ile ürün bilgileri çekildi:")
            print(f"  📦 Ad: {product_data.get('name', 'Bulunamadı')}")
            print(f"  💰 Fiyat: {product_data.get('current_price', 'Bulunamadı')} TL")
            print(f"  💸 Orijinal Fiyat: {product_data.get('original_price', 'Bulunamadı')} TL")
            print(f"  🖼️ Resim: {'Var' if product_data.get('image_url') else 'Yok'}")
            print(f"  🔗 Final URL: {product_data.get('url', 'Bulunamadı')}")
            
            print(f"\n✅ Bu mobil link ile bot komutunu kullanabilirsiniz!")
            print(f"Discord'da: !ekle {test_link}")
            print(f"Web UI'de: URL kutusuna {test_link}")
            
            return True
        else:
            print("\n❌ BAŞARISIZ! Ürün bilgileri çekilemedi")
            if product_data:
                print(f"  Hata: {product_data.get('error', 'Bilinmeyen hata')}")
            
            print(f"\n💡 Alternatif çözümler:")
            print(f"  1. Manuel ekleme: !manuel_ekle \"Ürün Adı\" fiyat \"{test_link}\"")
            print(f"  2. Tam URL'yi kullanın: {full_url}")
            print(f"  3. Direkt ürün ID'si: {product_id}")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Test sırasında hata: {e}")
        return False

def show_mobile_usage():
    """Mobil kullanım örneklerini gösterir"""
    print("\n=== MOBİL KULLANIM ÖRNEKLERİ ===")
    
    print("📱 MOBİL UYGULAMADAN PAYLAŞIM:")
    print("  1. Trendyol mobil uygulamasını açın")
    print("  2. Takip etmek istediğiniz ürüne gidin")
    print("  3. 'Paylaş' butonuna tıklayın")
    print("  4. 'Linki Kopyala' seçeneğini seçin")
    print("  5. Kopyalanan ty.gl linkini bot'a verin")
    
    print("\n🤖 BOT KOMUTLARI:")
    print("  !ekle https://ty.gl/reii1wcijhbf1")
    print("  /ekle https://ty.gl/reii1wcijhbf1")
    print("  !manuel_ekle \"Ürün Adı\" 299.99 \"https://ty.gl/abc123\"")
    
    print("\n🌐 WEB UI:")
    print("  1. http://localhost:5001 adresine gidin")
    print("  2. 'Ürün Ekle' sayfasına gidin")
    print("  3. URL kutusuna ty.gl linkini yapıştırın")
    print("  4. 'URL'yi Test Et' butonuna tıklayın")
    print("  5. Başarılı olursa 'Ürünü Ekle' butonuna tıklayın")
    
    print("\n✨ AVANTAJLAR:")
    print("  ✅ Mobil uygulamadan kolay paylaşım")
    print("  ✅ Kısa ve temiz linkler")
    print("  ✅ Otomatik redirect takibi")
    print("  ✅ Tam uyumluluk")

if __name__ == "__main__":
    show_mobile_usage()
    success = test_real_mobile_link()
    
    if success:
        print("\n🎉 MOBİL LİNK DESTEĞİ TAMAMEN ÇALIŞIYOR!")
        print("Artık ty.gl linklerini kullanabilirsiniz!")
    else:
        print("\n⚠️ Mobil link test edildi, manuel alternatifler mevcut")
    
    print("\n=== TEST TAMAMLANDI ===")