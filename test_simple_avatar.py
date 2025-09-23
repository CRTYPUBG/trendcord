#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basit Avatar Test
Discord avatar URL'lerini test eder
"""

def test_avatar_creation():
    """Avatar URL oluşturmayı test et"""
    print("=" * 50)
    print("Basit Avatar URL Test")
    print("=" * 50)
    
    # Test verileri
    discord_id = "831185933117423656"
    
    # Avatar hash'i olmadan (default avatar)
    try:
        default_id = (int(discord_id) >> 22) % 6
    except:
        default_id = 0
    
    default_avatar = f"https://cdn.discordapp.com/embed/avatars/{default_id}.png"
    print(f"Default Avatar: {default_avatar}")
    
    # Örnek avatar hash'i ile
    avatar_hash = "a1b2c3d4e5f6"
    custom_avatar = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.png"
    print(f"Custom Avatar: {custom_avatar}")
    
    # Animated avatar
    animated_hash = "a_1b2c3d4e5f6"
    animated_avatar = f"https://cdn.discordapp.com/avatars/{discord_id}/{animated_hash}.gif"
    print(f"Animated Avatar: {animated_avatar}")
    
    print()
    print("Bu URL'leri tarayıcıda test edebilirsin!")
    print("Default avatar her zaman çalışmalı.")

if __name__ == '__main__':
    test_avatar_creation()