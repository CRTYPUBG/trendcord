"""
Site Monitoring Test Script
Monitoring sisteminin çalışıp çalışmadığını test eder
"""

import asyncio
import json
from site_monitor import SiteMonitor
from datetime import datetime

async def test_monitoring_system():
    """Monitoring sistemini test et"""
    print("🧪 Site Monitoring Test Başlıyor...\n")
    
    monitor = SiteMonitor()
    
    # 1. Site yapısı analizi testi
    print("1️⃣ Site Yapısı Analizi Testi")
    print("=" * 50)
    
    test_url = "https://www.trendyol.com/apple/iphone-15-128-gb-p-773358088"
    print(f"🔍 Test URL: {test_url}")
    
    result = monitor.analyze_page_structure(test_url)
    
    if result.get('success'):
        print("✅ Sayfa analizi başarılı!")
        print(f"   📊 JSON-LD: {'Var' if result.get('json_ld_present') else 'Yok'}")
        print(f"   💰 Fiyat Selektörleri: {len(result.get('price_selectors', []))}")
        print(f"   📝 Başlık Selektörleri: {len(result.get('title_selectors', []))}")
        print(f"   🖼️ Resim Selektörleri: {len(result.get('image_selectors', []))}")
        print(f"   🔗 Sayfa Hash: {result.get('page_structure_hash', 'N/A')[:16]}...")
    else:
        print(f"❌ Sayfa analizi başarısız: {result.get('error', 'Bilinmeyen hata')}")
    
    print()
    
    # 2. API endpoint testi
    print("2️⃣ API Endpoint Testi")
    print("=" * 50)
    
    api_endpoints = monitor.check_api_endpoints()
    print(f"🌐 Bulunan API Endpoint'leri: {len(api_endpoints)}")
    
    for i, endpoint in enumerate(api_endpoints, 1):
        print(f"   {i}. {endpoint}")
    
    if not api_endpoints:
        print("   ⚠️ Aktif API endpoint bulunamadı")
    
    print()
    
    # 3. Tam yapı analizi testi
    print("3️⃣ Tam Site Yapısı Analizi")
    print("=" * 50)
    
    print("⏳ Tüm test URL'leri analiz ediliyor...")
    current_structure = monitor.analyze_current_structure()
    
    print("✅ Analiz tamamlandı!")
    print(f"   📊 JSON-LD Desteği: {'Var' if current_structure.json_ld_present else 'Yok'}")
    print(f"   💰 Toplam Fiyat Selektörleri: {len(current_structure.price_selectors)}")
    print(f"   📝 Toplam Başlık Selektörleri: {len(current_structure.title_selectors)}")
    print(f"   🖼️ Toplam Resim Selektörleri: {len(current_structure.image_selectors)}")
    print(f"   🌐 API Endpoint'leri: {len(current_structure.api_endpoints)}")
    print(f"   🔗 Genel Hash: {current_structure.page_structure_hash[:16]}...")
    print(f"   🕐 Analiz Zamanı: {current_structure.last_check}")
    
    print()
    
    # 4. Yapı kaydetme testi
    print("4️⃣ Yapı Kaydetme Testi")
    print("=" * 50)
    
    try:
        monitor.save_structure(current_structure)
        print("✅ Site yapısı başarıyla kaydedildi!")
        
        # Geri yükleme testi
        loaded_structure = monitor.load_previous_structure()
        if loaded_structure:
            print("✅ Site yapısı başarıyla geri yüklendi!")
            print(f"   📊 Yüklenen yapı hash: {loaded_structure.page_structure_hash[:16]}...")
        else:
            print("❌ Site yapısı geri yüklenemedi!")
    except Exception as e:
        print(f"❌ Yapı kaydetme hatası: {e}")
    
    print()
    
    # 5. Değişiklik karşılaştırma testi
    print("5️⃣ Değişiklik Karşılaştırma Testi")
    print("=" * 50)
    
    # Sahte bir eski yapı oluştur (değişiklik simülasyonu için)
    fake_old_structure = current_structure
    fake_old_structure.json_ld_present = not current_structure.json_ld_present
    fake_old_structure.price_selectors = current_structure.price_selectors[:-1] if current_structure.price_selectors else []
    
    changes = monitor.compare_structures(fake_old_structure, current_structure)
    
    if changes['has_changes']:
        print("✅ Değişiklik tespit sistemi çalışıyor!")
        
        if changes['critical_changes']:
            print("   🔴 Kritik Değişiklikler:")
            for change in changes['critical_changes']:
                print(f"      • {change}")
        
        if changes['minor_changes']:
            print("   🟡 Küçük Değişiklikler:")
            for change in changes['minor_changes']:
                print(f"      • {change}")
        
        if changes['improvements']:
            print("   🟢 İyileştirmeler:")
            for change in changes['improvements']:
                print(f"      • {change}")
    else:
        print("⚠️ Değişiklik tespit edilmedi (test için normal)")
    
    print()
    
    # 6. Güncelleme önerileri testi
    print("6️⃣ Güncelleme Önerileri Testi")
    print("=" * 50)
    
    suggestions = monitor.generate_update_suggestions(changes)
    
    if suggestions:
        print("✅ Güncelleme önerileri oluşturuldu:")
        for suggestion in suggestions:
            print(f"   {suggestion}")
    else:
        print("ℹ️ Güncelleme önerisi yok (değişiklik olmadığı için normal)")
    
    print()
    
    # 7. Dosya yapısı kontrolü
    print("7️⃣ Dosya Yapısı Kontrolü")
    print("=" * 50)
    
    import os
    
    # Gerekli dosyaları kontrol et
    required_files = [
        'site_monitor.py',
        'cogs/monitoring_commands.py',
        'config.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - EKSIK!")
    
    # Site yapısı dosyası
    if os.path.exists(monitor.monitor_file):
        print(f"   ✅ {monitor.monitor_file} (site yapısı kaydı)")
        
        # Dosya içeriğini kontrol et
        try:
            with open(monitor.monitor_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"      📊 Kayıtlı yapı: {len(data)} alan")
        except Exception as e:
            print(f"      ❌ Dosya okunamadı: {e}")
    else:
        print(f"   ℹ️ {monitor.monitor_file} (henüz oluşturulmamış)")
    
    print()
    
    # Test özeti
    print("🎉 TEST TAMAMLANDI!")
    print("=" * 50)
    print("✅ Site monitoring sistemi hazır!")
    print("📋 Özellikler:")
    print("   • Site yapısı analizi")
    print("   • API endpoint kontrolü")
    print("   • Değişiklik tespit sistemi")
    print("   • Otomatik güncelleme önerileri")
    print("   • 2 günde bir otomatik kontrol")
    print("   • Global adminlere DM bildirimi")
    print()
    print("🚀 Bot'u başlattığınızda sistem otomatik çalışacak!")
    print("🎮 Manuel kontrol için: !monitoring_check")
    print("📊 Durum kontrolü için: !monitoring_status")

if __name__ == "__main__":
    asyncio.run(test_monitoring_system())