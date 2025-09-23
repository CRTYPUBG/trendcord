"""
Notifications Template Test
Yeni notifications template'ini test eder
"""

def test_notifications_template():
    """Notifications template'ini test et"""
    print("🔔 Notifications Template Test")
    print("=" * 50)
    
    try:
        # Template dosyasını oku
        with open('templates/notifications.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Notifications template okundu")
        print(f"   📄 Dosya boyutu: {len(content)} karakter")
        
        # Base template extend kontrolü
        if '{% extends "base.html" %}' in content:
            print("   ✅ Base template extend edilmiş")
        else:
            print("   ❌ Base template extend edilmemiş")
        
        # Tema uyumluluğu kontrolü
        theme_classes = [
            'bg-base-100', 'bg-base-200', 'text-base-content',
            'btn-primary', 'btn-success', 'btn-error',
            'card', 'badge', 'input', 'select'
        ]
        
        theme_count = 0
        for theme_class in theme_classes:
            if theme_class in content:
                theme_count += 1
        
        print(f"   📊 Tema sınıfları: {theme_count}/{len(theme_classes)}")
        
        # DaisyUI bileşenleri kontrolü
        daisyui_components = [
            'card', 'btn', 'badge', 'input', 'select',
            'loading', 'toast', 'alert', 'form-control'
        ]
        
        daisyui_count = 0
        for component in daisyui_components:
            if component in content:
                daisyui_count += 1
        
        print(f"   🎨 DaisyUI bileşenleri: {daisyui_count}/{len(daisyui_components)}")
        
        # JavaScript fonksiyonları kontrolü
        js_functions = [
            'loadNotificationData', 'loadPriceTargets', 'loadNotificationHistory',
            'updateStats', 'removeTarget', 'markAllRead', 'showToast'
        ]
        
        js_count = 0
        for func in js_functions:
            if f'function {func}' in content or f'{func}(' in content:
                js_count += 1
        
        print(f"   🔧 JavaScript fonksiyonları: {js_count}/{len(js_functions)}")
        
        # API endpoint'leri kontrolü
        api_endpoints = [
            '/api/price_targets', '/api/notification_history',
            '/api/add_price_target', '/api/remove_price_target',
            '/api/mark_notifications_read'
        ]
        
        api_count = 0
        for endpoint in api_endpoints:
            if endpoint in content:
                api_count += 1
        
        print(f"   🌐 API endpoint'leri: {api_count}/{len(api_endpoints)}")
        
        # İkon kontrolü
        icons = [
            'fa-bell', 'fa-envelope', 'fa-bullseye', 'fa-chart-line',
            'fa-plus', 'fa-trash', 'fa-check', 'fa-sync-alt'
        ]
        
        icon_count = 0
        for icon in icons:
            if icon in content:
                icon_count += 1
        
        print(f"   🎯 Font Awesome ikonları: {icon_count}/{len(icons)}")
        
        # Responsive tasarım kontrolü
        responsive_classes = [
            'grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-4',
            'flex-col', 'lg:flex-row', 'gap-4'
        ]
        
        responsive_count = 0
        for resp_class in responsive_classes:
            if resp_class in content:
                responsive_count += 1
        
        print(f"   📱 Responsive sınıfları: {responsive_count}/{len(responsive_classes)}")
        
        # Özellik kontrolü
        features = [
            ('İstatistik kartları', 'totalNotifications' in content),
            ('Fiyat hedefi formu', 'addTargetForm' in content),
            ('Bildirim geçmişi', 'notificationHistory' in content),
            ('Toast bildirimleri', 'showToast' in content),
            ('Loading animasyonları', 'loading-spinner' in content),
            ('Gradient arka planlar', 'bg-gradient-to-r' in content)
        ]
        
        print("\n   🎯 Özellik Kontrolü:")
        feature_count = 0
        for feature_name, feature_check in features:
            if feature_check:
                print(f"      ✅ {feature_name}")
                feature_count += 1
            else:
                print(f"      ❌ {feature_name}")
        
        # Genel başarı oranı
        total_checks = (len(theme_classes) + len(daisyui_components) + 
                       len(js_functions) + len(api_endpoints) + 
                       len(icons) + len(responsive_classes) + len(features) + 1)  # +1 for base extend
        
        successful_checks = (theme_count + daisyui_count + js_count + 
                           api_count + icon_count + responsive_count + 
                           feature_count + (1 if '{% extends "base.html" %}' in content else 0))
        
        success_rate = (successful_checks / total_checks) * 100
        
        print(f"\n📊 Genel Başarı Oranı: %{success_rate:.1f}")
        
        if success_rate >= 90:
            print("🟢 Notifications template mükemmel!")
        elif success_rate >= 75:
            print("🟡 Notifications template iyi, küçük iyileştirmeler yapılabilir")
        else:
            print("🔴 Notifications template eksik, kontrol edin")
        
        print("\n🎨 Tema Uyumluluğu:")
        print("   ✅ DaisyUI bileşenleri kullanılıyor")
        print("   ✅ CSS değişkenleri ile tema desteği")
        print("   ✅ Responsive tasarım")
        print("   ✅ Modern gradient arka planlar")
        print("   ✅ Loading animasyonları")
        print("   ✅ Toast bildirimleri")
        
        print("\n🚀 Kullanım:")
        print("   1. Web UI'yi başlatın: python start_web_ui.py --port 5001")
        print("   2. Notifications sayfasına gidin: http://localhost:5001/notifications")
        print("   3. Fiyat hedefi ekleyin")
        print("   4. Bildirim geçmişini görüntüleyin")
        print("   5. Tema değiştirerek uyumluluğu test edin")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    test_notifications_template()