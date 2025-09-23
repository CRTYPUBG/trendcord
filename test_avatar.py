#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Avatar URL Test Scripti
Discord avatar URL'lerinin doğru oluşturulduğunu test eder
"""

from avatar_helper import get_discord_avatar_url, extract_avatar_info_from_discord_data

def test_avatar_urls():
    """Avatar URL'lerini test et"""
    print("=" * 50)
    print("Discord Avatar URL Test")
    print("=" * 50)
    
    # Test kullanıcı ID'si (senin ID'n)
    user_id = "831185933117423656"
    
    # Avatar hash'i olmadan (default avatar)
    default_avatar = get_discord_avatar_url(user_id, None)
    print(f"Default Avatar: {default_avatar}")
    
    # Örnek avatar hash'i ile
    example_hash = "a1b2c3d4e5f6"
    custom_avatar = get_discord_avatar_url(user_id, example_hash)
    print(f"Custom Avatar: {custom_avatar}")
    
    # Animated avatar hash'i ile
    animated_hash = "a_1b2c3d4e5f6"
    animated_avatar = get_discord_avatar_url(user_id, animated_hash)
    print(f"Animated Avatar: {animated_avatar}")
    
    print()
    print("Test Discord API verisi:")
    
    # Örnek Discord API verisi
    test_user_data = {
        'id': user_id,
        'username': 'TestUser',
        'avatar': None,  # Avatar hash'i buraya gelecek
        'discriminator': '0'
    }
    
    avatar_info = extract_avatar_info_from_discord_data(test_user_data)
    print(f"Avatar Info: {avatar_info}")
    
    print()
    print("Gerçek avatar hash'ini almak için:")
    print("1. Discord'da Developer Mode'u aç")
    print("2. Kendi profiline sağ tıkla → 'Kullanıcı ID'sini Kopyala'")
    print("3. Discord API'den kullanıcı bilgilerini çek:")
    print(f"   https://discord.com/api/v10/users/{user_id}")
    print("   (Bu için bot token veya OAuth token gerekli)")

if __name__ == '__main__':
    test_avatar_urls()