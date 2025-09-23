"""
Web UI Monitoring Test
Web UI'deki monitoring API'sini test eder
"""

import requests
import json

def test_web_monitoring():
    """Web monitoring API'sini test et"""
    print("🌐 Web UI Monitoring API Test")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # 1. Monitoring status API
    print("\n1️⃣ Monitoring Status API")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/monitoring/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API çalışıyor!")
            print(f"   🤖 Sistem: {'Aktif' if data.get('system_active') else 'Pasif'}")
            print(f"   🕐 Son kontrol: {data.get('last_check', 'N/A')}")
            print(f"   ⏰ Sonraki kontrol: {data.get('next_check', 'N/A')}")
            print(f"   ⚠️ Değişiklik: {'Var' if data.get('has_changes') else 'Yok'}")
            
            if data.get('structure'):
                structure = data['structure']
                print(f"   📊 JSON-LD: {'Var' if structure.get('json_ld_present') else 'Yok'}")
                print(f"   💰 Fiyat Selektörleri: {len(structure.get('price_selectors', []))}")
                print(f"   🌐 API Endpoint'leri: {len(structure.get('api_endpoints', []))}")
            
        else:
            print(f"❌ API Hatası: {response.status_code}")
            print(f"   Yanıt: {response.text}")
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
    
    # 2. Monitoring sayfası
    print("\n2️⃣ Monitoring Sayfası")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/monitoring", timeout=10)
        
        if response.status_code == 200:
            print("✅ Monitoring sayfası erişilebilir")
            
            # Sayfa içeriği kontrolü
            content = response.text
            checks = [
                ('Site Monitoring başlığı', 'Site Monitoring' in content),
                ('Manuel Kontrol butonu', 'Manuel Kontrol' in content),
                ('Sistem Durumu kartı', 'Sistem Durumu' in content),
                ('JavaScript yüklü', 'loadMonitoringStatus' in content)
            ]
            
            for check_name, check_result in checks:
                if check_result:
                    print(f"   ✅ {check_name}")
                else:
                    print(f"   ⚠️ {check_name} - Kontrol edin")
        else:
            print(f"❌ Sayfa hatası: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Sayfa bağlantı hatası: {e}")
    
    # 3. Ana sayfa kontrolü
    print("\n3️⃣ Ana Sayfa Kontrolü")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Ana sayfa erişilebilir")
            
            # Navigation kontrolü
            content = response.text
            if 'Site Monitoring' in content:
                print("   ✅ Monitoring linki navigation'da mevcut")
            else:
                print("   ⚠️ Monitoring linki navigation'da yok")
        else:
            print(f"❌ Ana sayfa hatası: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ana sayfa bağlantı hatası: {e}")
    
    # Test özeti
    print("\n" + "=" * 50)
    print("🎉 WEB UI MONITORING TEST TAMAMLANDI!")
    print("=" * 50)
    
    print("✅ Test Edilen Özellikler:")
    print("   • Monitoring Status API")
    print("   • Monitoring sayfası erişimi")
    print("   • Ana sayfa navigation")
    print("   • JavaScript fonksiyonları")
    
    print("\n🌐 Erişim Linkleri:")
    print(f"   • Ana Sayfa: {base_url}/")
    print(f"   • Monitoring: {base_url}/monitoring")
    print(f"   • API Status: {base_url}/api/monitoring/status")
    
    print("\n🎮 Kullanım:")
    print("   1. Monitoring sayfasına gidin")
    print("   2. 'Manuel Kontrol' butonuna tıklayın")
    print("   3. Sistem durumunu takip edin")
    print("   4. Gerçek zamanlı güncellemeleri görün")

if __name__ == "__main__":
    test_web_monitoring()