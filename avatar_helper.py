#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Discord Avatar URL Yardımcısı
Discord kullanıcı avatarlarını doğru şekilde oluşturur
"""

def get_discord_avatar_url(user_id, avatar_hash=None, size=128):
    """
    Discord kullanıcısının avatar URL'sini oluşturur
    
    Args:
        user_id (str): Discord kullanıcı ID'si
        avatar_hash (str): Avatar hash'i (None ise default avatar)
        size (int): Avatar boyutu (16, 32, 64, 128, 256, 512, 1024, 2048, 4096)
    
    Returns:
        str: Avatar URL'si
    """
    base_url = "https://cdn.discordapp.com"
    
    if avatar_hash:
        # Kullanıcının özel avatarı var
        # Animated avatar kontrolü (gif için 'a_' ile başlar)
        if avatar_hash.startswith('a_'):
            extension = 'gif'
        else:
            extension = 'png'
        
        return f"{base_url}/avatars/{user_id}/{avatar_hash}.{extension}?size={size}"
    else:
        # Default avatar kullan
        # Discord'un yeni sisteminde default avatar hesaplama
        try:
            user_id_int = int(user_id)
            # Yeni sistem: (user_id >> 22) % 6
            default_avatar_id = (user_id_int >> 22) % 6
        except (ValueError, TypeError):
            # Fallback: user_id'nin son rakamına göre
            default_avatar_id = int(str(user_id)[-1]) % 5
        
        return f"{base_url}/embed/avatars/{default_avatar_id}.png?size={size}"

def get_guild_icon_url(guild_id, icon_hash=None, size=128):
    """
    Discord sunucusunun icon URL'sini oluşturur
    
    Args:
        guild_id (str): Discord sunucu ID'si
        icon_hash (str): Icon hash'i (None ise default icon yok)
        size (int): Icon boyutu
    
    Returns:
        str: Icon URL'si veya None
    """
    if not icon_hash:
        return None
    
    base_url = "https://cdn.discordapp.com"
    
    # Animated icon kontrolü
    if icon_hash.startswith('a_'):
        extension = 'gif'
    else:
        extension = 'png'
    
    return f"{base_url}/icons/{guild_id}/{icon_hash}.{extension}?size={size}"

def extract_avatar_info_from_discord_data(user_data):
    """
    Discord API'den gelen kullanıcı verisinden avatar bilgilerini çıkarır
    
    Args:
        user_data (dict): Discord API'den gelen kullanıcı verisi
    
    Returns:
        dict: Avatar bilgileri
    """
    user_id = str(user_data.get('id', ''))
    avatar_hash = user_data.get('avatar')
    
    return {
        'user_id': user_id,
        'avatar_hash': avatar_hash,
        'avatar_url': get_discord_avatar_url(user_id, avatar_hash),
        'avatar_url_large': get_discord_avatar_url(user_id, avatar_hash, 512),
        'has_custom_avatar': bool(avatar_hash)
    }