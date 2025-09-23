"""
Tema Sistemi Test
Base template'deki tema sistemini test eder
"""

def test_theme_system():
    """Tema sistemini test et"""
    print("🎨 Tema Sistemi Test")
    print("=" * 40)
    
    # Base template'i kontrol et
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tema kontrolü
        themes = ['dark', 'light', 'cyberpunk', 'ocean', 'sunset']
        
        print("✅ Base template okundu")
        print(f"   📄 Dosya boyutu: {len(content)} karakter")
        
        theme_count = 0
        for theme in themes:
            if f'[data-theme="{theme}"]' in content:
                print(f"   ✅ {theme.capitalize()} teması tanımlı")
                theme_count += 1
            else:
                print(f"   ❌ {theme.capitalize()} teması eksik")
        
        # JavaScript fonksiyonu kontrolü
        if 'function setTheme' in content:
            print("   ✅ setTheme fonksiyonu mevcut")
        else:
            print("   ❌ setTheme fonksiyonu eksik")
        
        # Tema seçici kontrolü
        if 'fas fa-palette' in content:
            print("   ✅ Tema seçici ikonu mevcut")
        else:
            print("   ❌ Tema seçici ikonu eksik")
        
        # CSS değişkenleri kontrolü
        css_vars = ['--primary', '--secondary', '--accent', '--base-100', '--base-200', '--base-300']
        css_var_count = 0
        
        for var in css_vars:
            if var in content:
                css_var_count += 1
        
        print(f"   📊 CSS değişkenleri: {css_var_count}/{len(css_vars)}")
        
        # Tema butonları kontrolü
        theme_buttons = 0
        for theme in themes:
            if f"setTheme('{theme}')" in content:
                theme_buttons += 1
        
        print(f"   🎮 Tema butonları: {theme_buttons}/{len(themes)}")
        
        print("\n🎨 Tema sistemi hazır!")
        print("📋 Mevcut temalar:")
        for theme in themes:
            print(f"   • {theme.capitalize()}")
        
        print("\n🎯 Kullanım:")
        print("   1. Web UI'yi açın: http://localhost:5001")
        print("   2. Sağ üst köşedeki palet ikonuna tıklayın")
        print("   3. İstediğiniz temayı seçin")
        print("   4. Tema otomatik olarak değişecek ve kaydedilecek")
        
        # Başarı oranı
        total_checks = len(themes) + len(css_vars) + 3  # themes + css_vars + setTheme + palette + buttons
        successful_checks = theme_count + css_var_count + (1 if 'function setTheme' in content else 0) + (1 if 'fas fa-palette' in content else 0) + (1 if theme_buttons == len(themes) else 0)
        
        success_rate = (successful_checks / total_checks) * 100
        
        print(f"\n📊 Başarı Oranı: %{success_rate:.1f}")
        
        if success_rate >= 90:
            print("🟢 Tema sistemi mükemmel!")
        elif success_rate >= 70:
            print("🟡 Tema sistemi iyi, küçük eksikler var")
        else:
            print("🔴 Tema sistemi eksik, kontrol edin")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    test_theme_system()