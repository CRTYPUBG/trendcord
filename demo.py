#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trendyol Bot Demo Scripti
Bot'un çalışan özelliklerini gösterir
"""

from database import Database
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_database():
    """Database işlemlerini demo eder"""
    print("=== DATABASE DEMO ===")
    
    try:
        # Database bağlantısı
        db = Database()
        print("✅ Database bağlantısı başarılı")
        
        # Demo ürün verisi
        demo_products = [
            {
                'product_id': 'demo_001',
                'name': 'iPhone 15 128GB',
                'url': 'https://www.trendyol.com/apple/iphone-15-p-123456',
                'image_url': 'https://example.com/iphone15.jpg',
                'current_price': 45999.99,
                'original_price': 49999.99,
                'success': True
            },
            {
                'product_id': 'demo_002', 
                'name': 'Samsung Galaxy S24',
                'url': 'https://www.trendyol.com/samsung/galaxy-s24-p-789123',
                'image_url': 'https://example.com/galaxy-s24.jpg',
                'current_price': 32999.99,
                'original_price': 35999.99,
                'success': True
            },
            {
                'product_id': 'demo_003',
                'name': 'MacBook Air M2',
                'url': 'https://www.trendyol.com/apple/macbook-air-m2-p-456789',
                'image_url': 'https://example.com/macbook-air.jpg',
                'current_price': 28999.99,
                'original_price': 31999.99,
                'success': True
            }
        ]
        
        # Demo ürünleri ekle
        print("\n--- Demo Ürünleri Ekleniyor ---")
        for product in demo_products:
            if db.add_product(product, 'demo_guild', 'demo_user', 'demo_channel'):
                print(f"✅ Eklendi: {product['name']} - {product['current_price']} TL")
            else:
                print(f"⚠️  Zaten mevcut: {product['name']}")
        
        # Ürünleri listele
        print("\n--- Eklenen Ürünler ---")
        products = db.get_all_products('demo_guild')
        for i, product in enumerate(products, 1):
            print(f"{i}. {product['name']}")
            print(f"   💰 Fiyat: {product['current_price']} TL")
            print(f"   🆔 ID: {product['product_id']}")
            print(f"   🔗 URL: {product['url']}")
            
            # İndirim hesapla
            if product['original_price'] > product['current_price']:
                discount = ((product['original_price'] - product['current_price']) / product['original_price']) * 100
                print(f"   🎯 İndirim: %{discount:.1f}")
            print()
        
        # Fiyat güncelleme demo
        print("--- Fiyat Güncelleme Demo ---")
        if products:
            demo_product = products[0]
            old_price = demo_product['current_price']
            new_price = old_price * 0.9  # %10 indirim
            
            if db.update_product_price(demo_product['product_id'], new_price):
                print(f"✅ Fiyat güncellendi: {demo_product['name']}")
                print(f"   Eski: {old_price:.2f} TL")
                print(f"   Yeni: {new_price:.2f} TL")
                print(f"   İndirim: {old_price - new_price:.2f} TL")
        
        # Fiyat geçmişi
        print("\n--- Fiyat Geçmişi ---")
        if products:
            history = db.get_price_history(products[0]['product_id'])
            print(f"{products[0]['name']} fiyat geçmişi:")
            for entry in history:
                print(f"  📅 {entry['date'][:16]}: {entry['price']:.2f} TL")
        
        # Temizlik
        print("\n--- Demo Verilerini Temizleme ---")
        for product in demo_products:
            if db.delete_product(product['product_id']):
                print(f"🗑️  Silindi: {product['name']}")
        
        db.close()
        print("\n✅ Database demo tamamlandı!")
        
    except Exception as e:
        print(f"❌ Database demo hatası: {e}")

def demo_commands():
    """Bot komutlarını demo eder"""
    print("\n=== BOT KOMUTLARI DEMO ===")
    
    print("📋 Kullanılabilir Komutlar:")
    print()
    
    print("🔹 PREFIX KOMUTLARI (!)")
    print("  !manuel_ekle \"Ürün Adı\" fiyat \"URL\"")
    print("  !takiptekiler")
    print("  !fiyat_guncelle ÜRÜN_ID yeni_fiyat")
    print("  !sil ÜRÜN_ID")
    print("  !bilgi ÜRÜN_ID")
    print("  !yardım")
    print()
    
    print("🔹 SLASH KOMUTLARI (/)")
    print("  /manuel_ekle")
    print("  /takiptekiler")
    print("  /fiyat_guncelle")
    print("  /sil")
    print("  /bilgi")
    print("  /yardim")
    print()
    
    print("📝 Örnek Kullanım:")
    print("  !manuel_ekle \"iPhone 15\" 45999.99 \"https://www.trendyol.com/apple/iphone-15-p-123456\"")
    print("  !fiyat_guncelle 123456 44999.99")
    print("  !takiptekiler")
    print("  !sil 123456")
    print()
    
    print("⚠️  Not: Otomatik ürün çekme (!ekle URL) şu anda Trendyol'un")
    print("   anti-bot korumaları nedeniyle sınırlı çalışmaktadır.")
    print("   Manuel ekleme özelliğini kullanmanız önerilir.")

def demo_setup():
    """Kurulum bilgilerini gösterir"""
    print("\n=== KURULUM DEMO ===")
    
    print("📦 Gerekli Dosyalar:")
    import os
    files_to_check = [
        '.env',
        'main.py',
        'database.py',
        'scraper.py',
        'trendyol_api.py',
        'cogs/product_commands.py',
        'cogs/manual_commands.py'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
    
    print("\n🔧 Kurulum Adımları:")
    print("  1. Discord token'ını .env dosyasına ekleyin")
    print("  2. Bot'u Discord sunucusuna davet edin")
    print("  3. python main.py ile başlatın")
    print("  4. Discord'da !yardım yazarak test edin")
    
    print("\n🚀 Hızlı Başlangıç:")
    print("  cd trendcord")
    print("  python main.py")

if __name__ == "__main__":
    print("🤖 TRENDYOL BOT DEMO")
    print("=" * 50)
    
    demo_setup()
    demo_database()
    demo_commands()
    
    print("\n" + "=" * 50)
    print("✅ Demo tamamlandı!")
    print("Bot'u başlatmak için: python main.py")
    print("Yardım için: DURUM_RAPORU.md dosyasını okuyun")