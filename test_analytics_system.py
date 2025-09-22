#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analitik ve bildirim sistemi test dosyası
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from price_analyzer import PriceAnalyzer
from notification_system import NotificationSystem
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_analytics_system():
    """Analitik sistemi test et"""
    print("🔍 Analitik Sistemi Test Ediliyor...")
    
    try:
        # Database bağlantısı
        db = Database("data/test_analytics.sqlite")
        analyzer = PriceAnalyzer(db)
        notification_system = NotificationSystem(db)
        
        print("✅ Veritabanı bağlantısı başarılı")
        
        # Test verisi ekle
        test_product = {
            'product_id': '123456789',
            'name': 'Test Ürün - Analitik',
            'url': 'https://www.trendyol.com/test-urun-p-123456789',
            'image_url': 'https://test.com/image.jpg',
            'current_price': 299.99,
            'original_price': 399.99,
            'success': True
        }
        
        # Ürünü ekle
        success = db.add_product(test_product, 'test_guild', 'test_user', 'test_channel')
        if success:
            print("✅ Test ürünü eklendi")
            
            # Fiyat geçmişi ekle (simülasyon)
            import time
            from datetime import datetime, timedelta
            
            prices = [399.99, 389.99, 379.99, 299.99, 289.99, 279.99, 299.99]
            for i, price in enumerate(prices):
                date = (datetime.now() - timedelta(days=6-i)).isoformat()
                db.cursor.execute('''
                    INSERT INTO price_history (product_id, price, date)
                    VALUES (?, ?, ?)
                ''', ('123456789', price, date))
            
            db.conn.commit()
            print("✅ Fiyat geçmişi eklendi")
            
            # Trend analizi test et
            trend_data = analyzer.get_price_trend('123456789', days=7)
            if trend_data:
                print(f"📈 Trend Analizi:")
                print(f"   - Trend: {trend_data['trend']}")
                print(f"   - Değişim: %{trend_data['change_percentage']:.1f}")
                print(f"   - Ortalama: ₺{trend_data['average_price']:.2f}")
                print(f"   - Min: ₺{trend_data['min_price']:.2f}")
                print(f"   - Max: ₺{trend_data['max_price']:.2f}")
                print("✅ Trend analizi başarılı")
            
            # En iyi fırsatlar test et
            deals = analyzer.get_best_deals(guild_id='test_guild', limit=5)
            print(f"🔥 En İyi Fırsatlar: {len(deals)} fırsat bulundu")
            
            # Fiyat uyarıları test et
            alerts = analyzer.get_price_alerts(guild_id='test_guild', threshold=5)
            print(f"🚨 Fiyat Uyarıları: {len(alerts)} uyarı bulundu")
            
            # Sunucu istatistikleri test et
            stats = analyzer.get_guild_statistics('test_guild')
            if stats:
                print(f"📊 Sunucu İstatistikleri:")
                print(f"   - Toplam ürün: {stats['total_products']}")
                print(f"   - Ortalama fiyat: ₺{stats['average_price']:.2f}")
                print("✅ İstatistikler başarılı")
            
            # Bildirim sistemi test et
            print("\n🔔 Bildirim Sistemi Test Ediliyor...")
            
            # Fiyat hedefi ekle
            target_success = notification_system.add_price_target(
                product_id='123456789',
                user_id='test_user',
                guild_id='test_guild',
                channel_id='test_channel',
                target_price=250.0,
                condition='below'
            )
            
            if target_success:
                print("✅ Fiyat hedefi eklendi")
                
                # Fiyat hedeflerini kontrol et
                triggered = notification_system.check_price_targets('123456789', 240.0)
                if triggered:
                    print(f"🎯 Fiyat hedefi tetiklendi: {len(triggered)} bildirim")
                    print("✅ Fiyat hedefi sistemi çalışıyor")
                
                # Kullanıcı hedeflerini getir
                user_targets = notification_system.get_user_price_targets('test_user', 'test_guild')
                print(f"📋 Kullanıcı hedefleri: {len(user_targets)} hedef")
                
                # Bildirim geçmişi
                notifications = notification_system.get_notification_history('test_user', 'test_guild')
                print(f"📬 Bildirim geçmişi: {len(notifications)} bildirim")
                
                # Günlük özet
                summary = notification_system.get_daily_summary('test_guild')
                if summary:
                    print(f"📊 Günlük Özet:")
                    print(f"   - Bugün eklenen: {summary['products_added_today']}")
                    print(f"   - Dün değişen: {summary['price_changes_yesterday']}")
                    print(f"   - En iyi fırsatlar: {len(summary['biggest_drops'])}")
                    print("✅ Günlük özet başarılı")
            
            # Test verisini temizle
            db.delete_product('123456789')
            print("🧹 Test verisi temizlendi")
            
        else:
            print("❌ Test ürünü eklenemedi")
        
        db.close()
        print("\n🎉 Tüm testler başarıyla tamamlandı!")
        return True
        
    except Exception as e:
        logger.error(f"Test sırasında hata: {e}")
        print(f"❌ Test hatası: {e}")
        return False

if __name__ == "__main__":
    test_analytics_system()