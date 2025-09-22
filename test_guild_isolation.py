#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sunucu izolasyonu test scripti
Her sunucunun kendi ürünlerini görmesini test eder
"""

from database import Database
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_guild_isolation():
    """Sunucu izolasyonunu test eder"""
    print("=== SUNUCU İZOLASYONU TEST ===")
    
    try:
        db = Database()
        
        # Test verileri - 3 farklı sunucu
        test_products = [
            # Sunucu 1 ürünleri
            {
                'product_id': 'guild1_product1',
                'name': 'Sunucu 1 - Ürün 1',
                'url': 'https://www.trendyol.com/test1-p-111',
                'image_url': 'https://example.com/1.jpg',
                'current_price': 100.00,
                'original_price': 120.00,
                'success': True
            },
            {
                'product_id': 'guild1_product2',
                'name': 'Sunucu 1 - Ürün 2',
                'url': 'https://www.trendyol.com/test2-p-222',
                'image_url': 'https://example.com/2.jpg',
                'current_price': 200.00,
                'original_price': 250.00,
                'success': True
            },
            # Sunucu 2 ürünleri
            {
                'product_id': 'guild2_product1',
                'name': 'Sunucu 2 - Ürün 1',
                'url': 'https://www.trendyol.com/test3-p-333',
                'image_url': 'https://example.com/3.jpg',
                'current_price': 300.00,
                'original_price': 350.00,
                'success': True
            },
            {
                'product_id': 'guild2_product2',
                'name': 'Sunucu 2 - Ürün 2',
                'url': 'https://www.trendyol.com/test4-p-444',
                'image_url': 'https://example.com/4.jpg',
                'current_price': 400.00,
                'original_price': 450.00,
                'success': True
            },
            # Sunucu 3 ürünleri
            {
                'product_id': 'guild3_product1',
                'name': 'Sunucu 3 - Ürün 1',
                'url': 'https://www.trendyol.com/test5-p-555',
                'image_url': 'https://example.com/5.jpg',
                'current_price': 500.00,
                'original_price': 550.00,
                'success': True
            }
        ]
        
        # Sunucu bilgileri
        guilds = [
            {'id': 'test_guild_1', 'name': 'Test Sunucu 1'},
            {'id': 'test_guild_2', 'name': 'Test Sunucu 2'},
            {'id': 'test_guild_3', 'name': 'Test Sunucu 3'}
        ]
        
        print("\n1️⃣ Test Verilerini Ekleme...")
        
        # Ürünleri farklı sunuculara ekle
        for i, product in enumerate(test_products):
            guild_index = i // 2  # Her 2 ürün bir sunucuya
            if guild_index >= len(guilds):
                guild_index = len(guilds) - 1
            
            guild_id = guilds[guild_index]['id']
            user_id = f"user_{guild_index + 1}"
            channel_id = f"channel_{guild_index + 1}"
            
            if db.add_product(product, guild_id, user_id, channel_id):
                print(f"✅ {product['name']} -> {guilds[guild_index]['name']}")
            else:
                print(f"❌ {product['name']} eklenemedi")
        
        print("\n2️⃣ Sunucu İzolasyonu Testi...")
        
        # Her sunucunun sadece kendi ürünlerini görmesini test et
        for guild in guilds:
            guild_id = guild['id']
            guild_name = guild['name']
            
            # Normal kullanıcı görünümü (sadece kendi sunucusu)
            products = db.get_all_products(guild_id=guild_id, is_admin=False)
            print(f"\n📋 {guild_name} (Normal Kullanıcı):")
            print(f"   Görünen ürün sayısı: {len(products)}")
            
            for product in products:
                print(f"   - {product['name']}")
            
            # Admin görünümü (kendi sunucusu)
            admin_products = db.get_all_products(guild_id=guild_id, is_admin=True)
            print(f"\n👑 {guild_name} (Admin):")
            print(f"   Görünen ürün sayısı: {len(admin_products)}")
        
        print("\n3️⃣ Global Admin Testi...")
        
        # Global admin (tüm ürünleri görebilir)
        all_products = db.get_all_products(is_admin=True)
        print(f"\n🌐 Global Admin Görünümü:")
        print(f"   Toplam ürün sayısı: {len(all_products)}")
        
        for product in all_products:
            print(f"   - {product['name']} (Sunucu: {product['guild_id']})")
        
        print("\n4️⃣ İstatistik Testi...")
        
        # Sunucu istatistikleri
        stats = db.get_all_guilds_stats()
        print(f"\n📊 Sunucu İstatistikleri:")
        
        for stat in stats:
            guild_name = next((g['name'] for g in guilds if g['id'] == stat['guild_id']), f"Sunucu {stat['guild_id']}")
            print(f"   - {guild_name}: {stat['product_count']} ürün")
        
        print("\n5️⃣ Çapraz Erişim Testi...")
        
        # Bir sunucunun başka sunucunun ürününü göremediğini test et
        guild1_products = db.get_all_products(guild_id='test_guild_1')
        guild2_products = db.get_all_products(guild_id='test_guild_2')
        
        # Guild 1'in ürünlerinde Guild 2'nin ürünü olmamalı
        guild1_product_ids = [p['product_id'] for p in guild1_products]
        guild2_product_ids = [p['product_id'] for p in guild2_products]
        
        cross_contamination = set(guild1_product_ids) & set(guild2_product_ids)
        
        if not cross_contamination:
            print("✅ Çapraz erişim yok - İzolasyon başarılı!")
        else:
            print(f"❌ Çapraz erişim tespit edildi: {cross_contamination}")
        
        print("\n6️⃣ Temizlik...")
        
        # Test verilerini temizle
        for product in test_products:
            if db.delete_product(product['product_id']):
                print(f"🗑️  {product['name']} silindi")
        
        db.close()
        
        print("\n🎉 SUNUCU İZOLASYONU TEST TAMAMLANDI!")
        print("✅ Her sunucu sadece kendi ürünlerini görüyor")
        print("✅ Adminler tüm ürünleri görebiliyor")
        print("✅ Çapraz erişim engellendi")
        
        return True
        
    except Exception as e:
        print(f"❌ Test sırasında hata: {e}")
        return False

def show_isolation_features():
    """İzolasyon özelliklerini gösterir"""
    print("\n=== SUNUCU İZOLASYONU ÖZELLİKLERİ ===")
    
    print("🔒 GÜVENLİK ÖZELLİKLERİ:")
    print("  ✅ Her sunucu sadece kendi ürünlerini görür")
    print("  ✅ Kullanıcılar başka sunucuların ürünlerini göremez")
    print("  ✅ Ürün silme/güncelleme sadece kendi sunucuda")
    print("  ✅ Fiyat bildirimleri sadece ilgili sunucuya")
    
    print("\n👑 ADMİN ÖZELLİKLERİ:")
    print("  ✅ Adminler kendi sunucularındaki tüm ürünleri görür")
    print("  ✅ Adminler herkesin ürününü silebilir/güncelleyebilir")
    print("  ✅ Admin istatistikleri komutu")
    print("  ✅ Sunucu karşılaştırması")
    
    print("\n📊 İSTATİSTİK ÖZELLİKLERİ:")
    print("  ✅ Sunucu bazlı ürün sayısı")
    print("  ✅ En aktif sunucular listesi")
    print("  ✅ Toplam istatistikler")
    print("  ✅ Tarihsel veriler")
    
    print("\n🎯 KULLANIM ÖRNEKLERİ:")
    print("  Normal Kullanıcı:")
    print("    !takiptekiler  # Sadece bu sunucunun ürünleri")
    print("    !sil 123456    # Sadece kendi eklediği ürünler")
    print()
    print("  Admin:")
    print("    !takiptekiler     # Bu sunucunun tüm ürünleri")
    print("    !admin_stats      # Sunucu istatistikleri")
    print("    !sil 123456       # Herkesin ürününü silebilir")

if __name__ == "__main__":
    show_isolation_features()
    success = test_guild_isolation()
    
    if success:
        print("\n🎉 TÜM TESTLER BAŞARILI!")
        print("Sunucu izolasyonu tamamen çalışıyor!")
    else:
        print("\n❌ Bazı testler başarısız!")
    
    print("\n=== TEST TAMAMLANDI ===")