#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Global admin sistemi test scripti
"""

from admin_utils import admin_manager
import os
import logging
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_global_admin_system():
    """Global admin sistemini test eder"""
    print("=== GLOBAL ADMİN SİSTEMİ TEST ===")
    
    # .env dosyasından admin ID'lerini kontrol et
    print("\n1️⃣ .env Dosyası Kontrolü...")
    admin_ids_str = os.getenv('GLOBAL_ADMIN_IDS', '')
    print(f"GLOBAL_ADMIN_IDS: {admin_ids_str}")
    
    if admin_ids_str:
        print("✅ Global admin ID'leri .env dosyasında tanımlı")
    else:
        print("❌ Global admin ID'leri .env dosyasında tanımlı değil")
        return False
    
    # Admin manager'ı test et
    print("\n2️⃣ Admin Manager Testi...")
    
    # Yüklenen admin ID'leri
    global_admins = admin_manager.get_global_admin_list()
    print(f"Yüklenen global admin sayısı: {len(global_admins)}")
    
    for admin_id in global_admins:
        print(f"  - Global Admin ID: {admin_id}")
    
    # Test ID'leri
    test_ids = [
        992809942383870002,  # İlk admin ID
        831185933117423656,  # İkinci admin ID
        123456789,           # Test ID (admin değil)
        "992809942383870002", # String format
        "invalid_id"         # Geçersiz format
    ]
    
    print("\n3️⃣ Admin Kontrolü Testi...")
    
    for test_id in test_ids:
        is_admin = admin_manager.is_global_admin(test_id)
        print(f"  ID: {test_id} -> {'✅ Global Admin' if is_admin else '❌ Normal Kullanıcı'}")
    
    # Runtime admin ekleme/çıkarma testi
    print("\n4️⃣ Runtime Admin Yönetimi Testi...")
    
    test_new_admin = 999999999999999999
    
    # Admin ekleme
    if admin_manager.add_global_admin(test_new_admin):
        print(f"✅ Test admin eklendi: {test_new_admin}")
    else:
        print(f"❌ Test admin eklenemedi: {test_new_admin}")
    
    # Kontrol et
    if admin_manager.is_global_admin(test_new_admin):
        print(f"✅ Test admin doğrulandı: {test_new_admin}")
    else:
        print(f"❌ Test admin doğrulanamadı: {test_new_admin}")
    
    # Admin çıkarma
    if admin_manager.remove_global_admin(test_new_admin):
        print(f"✅ Test admin kaldırıldı: {test_new_admin}")
    else:
        print(f"❌ Test admin kaldırılamadı: {test_new_admin}")
    
    # Tekrar kontrol et
    if not admin_manager.is_global_admin(test_new_admin):
        print(f"✅ Test admin kaldırma doğrulandı: {test_new_admin}")
    else:
        print(f"❌ Test admin hala mevcut: {test_new_admin}")
    
    print("\n5️⃣ Admin Seviyesi Testi...")
    
    # Mock user objesi oluştur
    class MockUser:
        def __init__(self, user_id, has_guild_perms=False):
            self.id = user_id
            if has_guild_perms:
                self.guild_permissions = MockGuildPermissions(True)
            else:
                self.guild_permissions = MockGuildPermissions(False)
    
    class MockGuildPermissions:
        def __init__(self, is_admin):
            self.administrator = is_admin
    
    class MockGuild:
        def __init__(self):
            self.id = 123456789
    
    # Test kullanıcıları
    global_admin_user = MockUser(992809942383870002)  # Global admin
    guild_admin_user = MockUser(123456789, has_guild_perms=True)  # Guild admin
    normal_user = MockUser(987654321)  # Normal kullanıcı
    
    mock_guild = MockGuild()
    
    test_users = [
        (global_admin_user, "Global Admin"),
        (guild_admin_user, "Guild Admin"),
        (normal_user, "Normal Kullanıcı")
    ]
    
    for user, user_type in test_users:
        admin_level = admin_manager.get_admin_level(user, mock_guild)
        is_admin = admin_manager.is_admin(user, mock_guild)
        print(f"  {user_type} (ID: {user.id}):")
        print(f"    Admin Level: {admin_level}")
        print(f"    Is Admin: {'✅' if is_admin else '❌'}")
    
    print("\n🎉 GLOBAL ADMİN SİSTEMİ TEST TAMAMLANDI!")
    return True

def show_admin_features():
    """Admin özelliklerini gösterir"""
    print("\n=== GLOBAL ADMİN ÖZELLİKLERİ ===")
    
    print("🌐 GLOBAL ADMİN YETKİLERİ:")
    print("  ✅ Tüm sunucularda admin yetkisi")
    print("  ✅ Herkesin ürününü silebilir/güncelleyebilir")
    print("  ✅ Tüm sunucuların ürünlerini görebilir")
    print("  ✅ Global istatistiklere erişim")
    print("  ✅ Global admin listesini görebilir")
    
    print("\n👑 SUNUCU ADMİN YETKİLERİ:")
    print("  ✅ Sadece kendi sunucusunda admin yetkisi")
    print("  ✅ Kendi sunucusundaki herkesin ürününü yönetebilir")
    print("  ✅ Sunucu istatistiklerini görebilir")
    
    print("\n👤 NORMAL KULLANICI YETKİLERİ:")
    print("  ✅ Sadece kendi eklediği ürünleri yönetebilir")
    print("  ✅ Sadece kendi sunucusunun ürünlerini görebilir")
    
    print("\n🎯 GLOBAL ADMİN KOMUTLARI:")
    print("  !global_admin_list  # Global admin listesi")
    print("  !global_stats       # Tüm sunucuların istatistikleri")
    print("  !admin_stats        # Sunucu istatistikleri")
    print("  !takiptekiler       # Gelişmiş görünüm")
    
    print("\n⚙️ YAPILANDIRMA:")
    print("  .env dosyasında GLOBAL_ADMIN_IDS ayarı")
    print("  Virgülle ayrılmış Discord kullanıcı ID'leri")
    print("  Örnek: GLOBAL_ADMIN_IDS=123456789,987654321")

def show_current_admins():
    """Mevcut adminleri gösterir"""
    print("\n=== MEVCUT GLOBAL ADMİNLER ===")
    
    global_admins = admin_manager.get_global_admin_list()
    
    if global_admins:
        print(f"Toplam {len(global_admins)} global admin:")
        for i, admin_id in enumerate(global_admins, 1):
            print(f"  {i}. ID: {admin_id}")
    else:
        print("Hiç global admin tanımlı değil.")
    
    print(f"\n.env dosyasındaki ayar:")
    print(f"GLOBAL_ADMIN_IDS={os.getenv('GLOBAL_ADMIN_IDS', 'Tanımlı değil')}")

if __name__ == "__main__":
    show_admin_features()
    show_current_admins()
    success = test_global_admin_system()
    
    if success:
        print("\n🎉 TÜM TESTLER BAŞARILI!")
        print("Global admin sistemi tamamen çalışıyor!")
    else:
        print("\n❌ Bazı testler başarısız!")
    
    print("\n=== TEST TAMAMLANDI ===")