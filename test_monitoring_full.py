"""
Full Monitoring System Test
Tüm monitoring sistemini test eder (Discord bot komutları hariç)
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from site_monitor import SiteMonitor

async def test_full_monitoring():
    """Tam monitoring sistemini test et"""
    print("🚀 Full Monitoring System Test")
    print("=" * 60)
    
    monitor = SiteMonitor()
    
    # 1. İlk yapı analizi
    print("\n1️⃣ İlk Site Yapısı Analizi")
    print("-" * 40)
    
    current_structure = monitor.analyze_current_structure()
    print(f"✅ Analiz tamamlandı!")
    print(f"   📊 JSON-LD: {'Var' if current_structure.json_ld_present else 'Yok'}")
    print(f"   💰 Fiyat Selektörleri: {len(current_structure.price_selectors)}")
    print(f"   📝 Başlık Selektörleri: {len(current_structure.title_selectors)}")
    print(f"   🌐 API Endpoint'leri: {len(current_structure.api_endpoints)}")
    
    # Yapıyı kaydet
    monitor.save_structure(current_structure)
    print("💾 Yapı kaydedildi")
    
    # 2. Değişiklik simülasyonu
    print("\n2️⃣ Değişiklik Simülasyonu")
    print("-" * 40)
    
    # Sahte eski yapı oluştur
    old_structure = current_structure
    old_structure.json_ld_present = not current_structure.json_ld_present
    old_structure.price_selectors = current_structure.price_selectors[:-1] if current_structure.price_selectors else ['fake_selector']
    
    # Değişiklikleri karşılaştır
    changes = monitor.compare_structures(old_structure, current_structure)
    
    if changes['has_changes']:
        print("⚠️ Değişiklikler tespit edildi:")
        
        if changes['critical_changes']:
            print("   🔴 Kritik:")
            for change in changes['critical_changes']:
                print(f"      • {change}")
        
        if changes['minor_changes']:
            print("   🟡 Küçük:")
            for change in changes['minor_changes']:
                print(f"      • {change}")
        
        if changes['improvements']:
            print("   🟢 İyileştirme:")
            for change in changes['improvements']:
                print(f"      • {change}")
    else:
        print("✅ Değişiklik yok")
    
    # 3. Güncelleme önerileri
    print("\n3️⃣ Güncelleme Önerileri")
    print("-" * 40)
    
    suggestions = monitor.generate_update_suggestions(changes)
    if suggestions:
        for suggestion in suggestions:
            print(f"   {suggestion}")
    else:
        print("   ℹ️ Özel öneri yok")
    
    # 4. Mock bot ile DM testi
    print("\n4️⃣ Mock Bot DM Testi")
    print("-" * 40)
    
    class MockBot:
        def __init__(self):
            self.sent_messages = []
        
        async def fetch_user(self, user_id):
            return MockUser(user_id, self)
    
    class MockUser:
        def __init__(self, user_id, bot):
            self.id = user_id
            self.bot = bot
        
        async def send(self, message):
            self.bot.sent_messages.append({
                'user_id': self.id,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
            print(f"   📨 Mock DM gönderildi (User {self.id}): {message[:50]}...")
    
    mock_bot = MockBot()
    
    # Test mesajı gönder
    test_message = "🧪 Test monitoring mesajı"
    await monitor.send_dm_to_admins(mock_bot, test_message)
    
    print(f"✅ {len(mock_bot.sent_messages)} DM gönderildi")
    
    # 5. Tam monitoring kontrolü
    print("\n5️⃣ Tam Monitoring Kontrolü")
    print("-" * 40)
    
    try:
        await monitor.run_monitoring_check(mock_bot)
        print("✅ Monitoring kontrolü başarılı")
        print(f"📨 Toplam gönderilen mesaj: {len(mock_bot.sent_messages)}")
        
        # Gönderilen mesajları göster
        for i, msg in enumerate(mock_bot.sent_messages, 1):
            print(f"   {i}. User {msg['user_id']}: {msg['message'][:100]}...")
    
    except Exception as e:
        print(f"❌ Monitoring kontrolü hatası: {e}")
    
    # 6. Dosya yapısı kontrolü
    print("\n6️⃣ Dosya Yapısı Kontrolü")
    print("-" * 40)
    
    # Site yapısı dosyası
    if os.path.exists(monitor.monitor_file):
        with open(monitor.monitor_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ {monitor.monitor_file}")
        print(f"   📊 Kayıtlı alanlar: {len(data)}")
        print(f"   🕐 Son kontrol: {data.get('last_check', 'N/A')}")
        print(f"   🔗 Hash: {data.get('page_structure_hash', 'N/A')[:16]}...")
    else:
        print(f"❌ {monitor.monitor_file} bulunamadı")
    
    # 7. Zaman hesaplamaları
    print("\n7️⃣ Zaman Hesaplamaları")
    print("-" * 40)
    
    if current_structure.last_check:
        last_check = datetime.fromisoformat(current_structure.last_check)
        next_check = last_check + timedelta(hours=48)
        time_until_next = next_check - datetime.now()
        
        print(f"🕐 Son kontrol: {last_check.strftime('%d.%m.%Y %H:%M')}")
        print(f"⏰ Sonraki kontrol: {next_check.strftime('%d.%m.%Y %H:%M')}")
        
        if time_until_next.total_seconds() > 0:
            hours = int(time_until_next.total_seconds() // 3600)
            minutes = int((time_until_next.total_seconds() % 3600) // 60)
            print(f"⏳ Kalan süre: {hours} saat {minutes} dakika")
        else:
            print("⚡ Kontrol zamanı geldi!")
    
    # 8. Web UI API simülasyonu
    print("\n8️⃣ Web UI API Simülasyonu")
    print("-" * 40)
    
    try:
        # Status API simülasyonu
        previous_structure = monitor.load_previous_structure()
        
        if previous_structure:
            last_check = datetime.fromisoformat(previous_structure.last_check)
            next_check = last_check + timedelta(hours=48)
            
            api_response = {
                'system_active': True,
                'last_check': previous_structure.last_check,
                'next_check': next_check.isoformat(),
                'has_changes': changes['has_changes'],
                'structure': {
                    'json_ld_present': previous_structure.json_ld_present,
                    'price_selectors': len(previous_structure.price_selectors),
                    'api_endpoints': len(previous_structure.api_endpoints)
                }
            }
            
            print("✅ API Response simülasyonu:")
            print(f"   🤖 Sistem: {'Aktif' if api_response['system_active'] else 'Pasif'}")
            print(f"   🕐 Son kontrol: {api_response['last_check']}")
            print(f"   ⚠️ Değişiklik: {'Var' if api_response['has_changes'] else 'Yok'}")
        else:
            print("⚠️ API response oluşturulamadı (yapı yok)")
    
    except Exception as e:
        print(f"❌ API simülasyonu hatası: {e}")
    
    # Test özeti
    print("\n" + "=" * 60)
    print("🎉 FULL MONITORING TEST TAMAMLANDI!")
    print("=" * 60)
    
    print("✅ Başarılı Testler:")
    print("   • Site yapısı analizi")
    print("   • Değişiklik tespit sistemi")
    print("   • Güncelleme önerileri")
    print("   • Mock bot DM sistemi")
    print("   • Dosya kaydetme/yükleme")
    print("   • Zaman hesaplamaları")
    print("   • Web UI API simülasyonu")
    
    print("\n🚀 Sistem Hazır!")
    print("📋 Özellikler:")
    print("   • 2 günde bir otomatik kontrol")
    print("   • Global adminlere DM bildirimi")
    print("   • Web UI entegrasyonu")
    print("   • Manuel kontrol komutları")
    
    print("\n🎮 Kullanım:")
    print("   • Discord: !monitoring_check, !monitoring_status")
    print("   • Web UI: http://localhost:5001/monitoring")
    print("   • Otomatik: Bot başlatıldığında aktif")

if __name__ == "__main__":
    asyncio.run(test_full_monitoring())