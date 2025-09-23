#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kullanıcı Kimlik Doğrulama ve Yetkilendirme Sistemi
Discord OAuth2 ile güvenli giriş ve kullanıcı yönetimi
"""

import os
import json
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests
import logging
from functools import wraps
from flask import session, request, jsonify, redirect, url_for

logger = logging.getLogger(__name__)

class UserEncryption:
    """Kullanıcı verilerini şifrelemek için uçtan uca şifreleme sistemi"""
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
    
    def _get_or_create_master_key(self):
        """Ana şifreleme anahtarını al veya oluştur"""
        key_file = "data/master.key"
        
        try:
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Yeni anahtar oluştur
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                logger.info("Yeni ana şifreleme anahtarı oluşturuldu")
                return key
        except Exception as e:
            logger.error(f"Ana anahtar işlemi hatası: {e}")
            # Geçici anahtar oluştur (güvenlik riski!)
            return Fernet.generate_key()
    
    def generate_user_key(self, user_id, password_hash):
        """Kullanıcı için özel şifreleme anahtarı oluştur"""
        try:
            # Kullanıcı ID ve şifre hash'ini birleştir
            combined = f"{user_id}:{password_hash}".encode()
            
            # PBKDF2 ile güçlü anahtar türet
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.master_key[:16],  # Ana anahtarın ilk 16 byte'ını salt olarak kullan
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(combined))
            return key
        except Exception as e:
            logger.error(f"Kullanıcı anahtarı oluşturma hatası: {e}")
            return None
    
    def encrypt_data(self, data, user_key):
        """Veriyi şifrele"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            elif not isinstance(data, str):
                data = str(data)
            
            fernet = Fernet(user_key)
            encrypted = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Veri şifreleme hatası: {e}")
            return None
    
    def decrypt_data(self, encrypted_data, user_key):
        """Veriyi çöz"""
        try:
            fernet = Fernet(user_key)
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Veri çözme hatası: {e}")
            return None

class DiscordOAuth:
    """Discord OAuth2 kimlik doğrulama sistemi"""
    
    def __init__(self):
        self.client_id = os.getenv('DISCORD_CLIENT_ID')
        self.client_secret = os.getenv('DISCORD_CLIENT_SECRET')
        self.redirect_uri = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/auth/callback')
        self.base_url = 'https://discord.com/api/v10'
        
        if not self.client_id or not self.client_secret:
            logger.warning("Discord OAuth bilgileri eksik! .env dosyasını kontrol edin.")
    
    def get_authorization_url(self):
        """Discord yetkilendirme URL'sini oluştur"""
        if not self.client_id:
            return None
        
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'identify guilds',
            'state': state
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"https://discord.com/api/oauth2/authorize?{query_string}"
    
    def exchange_code(self, code, state):
        """Yetkilendirme kodunu access token ile değiştir"""
        try:
            # State kontrolü
            if state != session.get('oauth_state'):
                logger.error("OAuth state uyumsuzluğu")
                return None
            
            # Token isteği
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri
            }
            
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            response = requests.post(
                f"{self.base_url}/oauth2/token",
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Token değişimi hatası: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"OAuth kod değişimi hatası: {e}")
            return None
    
    def get_user_info(self, access_token):
        """Kullanıcı bilgilerini al"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Kullanıcı bilgileri
            user_response = requests.get(
                f"{self.base_url}/users/@me",
                headers=headers,
                timeout=10
            )
            
            if user_response.status_code != 200:
                return None
            
            user_data = user_response.json()
            
            # Kullanıcının sunucuları
            guilds_response = requests.get(
                f"{self.base_url}/users/@me/guilds",
                headers=headers,
                timeout=10
            )
            
            guilds_data = []
            if guilds_response.status_code == 200:
                guilds_data = guilds_response.json()
            
            return {
                'user': user_data,
                'guilds': guilds_data
            }
            
        except Exception as e:
            logger.error(f"Kullanıcı bilgisi alma hatası: {e}")
            return None

class UserManager:
    """Kullanıcı yönetimi ve yetkilendirme sistemi"""
    
    def __init__(self, db):
        self.db = db
        self.encryption = UserEncryption()
        self.oauth = DiscordOAuth()
        self._create_user_tables()
    
    def _create_user_tables(self):
        """Kullanıcı tablolarını oluştur"""
        try:
            # Kullanıcılar tablosu
            self.db.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                discriminator TEXT,
                avatar TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                encryption_key_hash TEXT,
                settings TEXT  -- Şifrelenmiş kullanıcı ayarları
            )
            ''')
            
            # Kullanıcı sunucuları tablosu
            self.db.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_guilds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                guild_id TEXT NOT NULL,
                guild_name TEXT,
                permissions INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            ''')
            
            # Kullanıcı oturumları tablosu
            self.db.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            ''')
            
            # Kullanıcı ürünleri tablosunu güncelle (şifreleme için)
            self.db.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                encrypted_data TEXT NOT NULL,  -- Şifrelenmiş ürün verisi
                guild_id TEXT,
                channel_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, product_id, guild_id)
            )
            ''')
            
            self.db.conn.commit()
            logger.info("Kullanıcı tabloları oluşturuldu")
            
        except Exception as e:
            logger.error(f"Kullanıcı tabloları oluşturma hatası: {e}")
    
    def create_or_update_user(self, discord_user_data, guilds_data):
        """Discord verilerinden kullanıcı oluştur veya güncelle"""
        try:
            discord_id = str(discord_user_data['id'])
            username = discord_user_data['username']
            discriminator = discord_user_data.get('discriminator', '0')
            avatar = discord_user_data.get('avatar')
            email = discord_user_data.get('email')
            
            # Avatar URL'sini oluştur
            if avatar:
                # Animated avatar kontrolü
                if avatar.startswith('a_'):
                    avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar}.gif"
                else:
                    avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar}.png"
            else:
                # Default avatar
                try:
                    default_id = (int(discord_id) >> 22) % 6
                except:
                    default_id = 0
                avatar_url = f"https://cdn.discordapp.com/embed/avatars/{default_id}.png"
            
            # Kullanıcı var mı kontrol et
            existing_user = self.db.cursor.execute(
                'SELECT id, encryption_key_hash FROM users WHERE discord_id = ?',
                (discord_id,)
            ).fetchone()
            
            now = datetime.now().isoformat()
            
            if existing_user:
                # Mevcut kullanıcıyı güncelle
                user_id = existing_user[0]
                self.db.cursor.execute('''
                UPDATE users SET 
                    username = ?, discriminator = ?, avatar = ?, 
                    email = ?, last_login = ?
                WHERE discord_id = ?
                ''', (username, discriminator, avatar_url, email, now, discord_id))
            else:
                # Yeni kullanıcı oluştur
                encryption_key_hash = hashlib.sha256(f"{discord_id}:{secrets.token_hex(32)}".encode()).hexdigest()
                
                self.db.cursor.execute('''
                INSERT INTO users 
                (discord_id, username, discriminator, avatar, email, last_login, encryption_key_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (discord_id, username, discriminator, avatar_url, email, now, encryption_key_hash))
                
                user_id = self.db.cursor.lastrowid
            
            # Kullanıcının sunucularını güncelle
            self._update_user_guilds(user_id, guilds_data)
            
            self.db.conn.commit()
            return user_id
            
        except Exception as e:
            logger.error(f"Kullanıcı oluşturma/güncelleme hatası: {e}")
            self.db.conn.rollback()
            return None
    
    def _update_user_guilds(self, user_id, guilds_data):
        """Kullanıcının sunucularını güncelle"""
        try:
            # Mevcut sunucuları pasif yap
            self.db.cursor.execute(
                'UPDATE user_guilds SET is_active = 0 WHERE user_id = ?',
                (user_id,)
            )
            
            # Yeni sunucuları ekle/güncelle
            for guild in guilds_data:
                guild_id = str(guild['id'])
                guild_name = guild['name']
                permissions = guild.get('permissions', 0)
                
                # Sunucu var mı kontrol et
                existing = self.db.cursor.execute(
                    'SELECT id FROM user_guilds WHERE user_id = ? AND guild_id = ?',
                    (user_id, guild_id)
                ).fetchone()
                
                if existing:
                    # Mevcut sunucuyu aktif yap
                    self.db.cursor.execute('''
                    UPDATE user_guilds SET 
                        guild_name = ?, permissions = ?, is_active = 1
                    WHERE user_id = ? AND guild_id = ?
                    ''', (guild_name, permissions, user_id, guild_id))
                else:
                    # Yeni sunucu ekle
                    self.db.cursor.execute('''
                    INSERT INTO user_guilds 
                    (user_id, guild_id, guild_name, permissions, is_active)
                    VALUES (?, ?, ?, ?, 1)
                    ''', (user_id, guild_id, guild_name, permissions))
            
        except Exception as e:
            logger.error(f"Kullanıcı sunucuları güncelleme hatası: {e}")
    
    def create_session(self, user_id, ip_address=None, user_agent=None):
        """Kullanıcı oturumu oluştur"""
        try:
            session_token = secrets.token_urlsafe(64)
            expires_at = (datetime.now() + timedelta(days=30)).isoformat()
            
            self.db.cursor.execute('''
            INSERT INTO user_sessions 
            (user_id, session_token, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_token, expires_at, ip_address, user_agent))
            
            self.db.conn.commit()
            return session_token
            
        except Exception as e:
            logger.error(f"Oturum oluşturma hatası: {e}")
            return None
    
    def validate_session(self, session_token):
        """Oturum doğrula"""
        try:
            result = self.db.cursor.execute('''
            SELECT u.id, u.discord_id, u.username, u.encryption_key_hash, s.expires_at, u.avatar
            FROM users u
            JOIN user_sessions s ON u.id = s.user_id
            WHERE s.session_token = ? AND s.expires_at > ? AND u.is_active = 1
            ''', (session_token, datetime.now().isoformat())).fetchone()
            
            if result:
                return {
                    'user_id': result[0],
                    'discord_id': result[1],
                    'username': result[2],
                    'encryption_key_hash': result[3],
                    'expires_at': result[4],
                    'avatar_url': result[5]
                }
            return None
            
        except Exception as e:
            logger.error(f"Oturum doğrulama hatası: {e}")
            return None
    
    def get_user_guilds(self, user_id):
        """Kullanıcının sunucularını al"""
        try:
            results = self.db.cursor.execute('''
            SELECT guild_id, guild_name, permissions
            FROM user_guilds
            WHERE user_id = ? AND is_active = 1
            ORDER BY guild_name
            ''', (user_id,)).fetchall()
            
            guilds = []
            for row in results:
                guilds.append({
                    'guild_id': row[0],
                    'guild_name': row[1],
                    'permissions': row[2]
                })
            
            return guilds
            
        except Exception as e:
            logger.error(f"Kullanıcı sunucuları alma hatası: {e}")
            return []
    
    def has_guild_access(self, user_id, guild_id):
        """Kullanıcının sunucuya erişimi var mı kontrol et"""
        try:
            result = self.db.cursor.execute('''
            SELECT id FROM user_guilds
            WHERE user_id = ? AND guild_id = ? AND is_active = 1
            ''', (user_id, guild_id)).fetchone()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Sunucu erişim kontrolü hatası: {e}")
            return False
    
    def is_global_admin(self, discord_id):
        """Kullanıcı global admin mi kontrol et"""
        try:
            from config import GLOBAL_ADMIN_IDS
            return str(discord_id) in GLOBAL_ADMIN_IDS
        except Exception as e:
            logger.error(f"Global admin kontrolü hatası: {e}")
            return False
    
    def logout_user(self, session_token):
        """Kullanıcı oturumunu sonlandır"""
        try:
            self.db.cursor.execute(
                'DELETE FROM user_sessions WHERE session_token = ?',
                (session_token,)
            )
            self.db.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Oturum sonlandırma hatası: {e}")
            return False

# Decorator'lar
def login_required(f):
    """Giriş gerekli decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = session.get('session_token')
        if not session_token:
            return redirect(url_for('login'))
        
        # Oturum doğrula
        from database import Database
        db = Database()
        user_manager = UserManager(db)
        
        user_data = user_manager.validate_session(session_token)
        db.close()
        
        if not user_data:
            session.clear()
            return redirect(url_for('login'))
        
        # Kullanıcı bilgilerini request'e ekle
        request.current_user = user_data
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Admin yetkisi gerekli decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'error': 'Giriş gerekli'}), 401
        
        from database import Database
        db = Database()
        user_manager = UserManager(db)
        
        is_admin = user_manager.is_global_admin(request.current_user['discord_id'])
        db.close()
        
        if not is_admin:
            return jsonify({'error': 'Admin yetkisi gerekli'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def guild_access_required(f):
    """Sunucu erişimi gerekli decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'error': 'Giriş gerekli'}), 401
        
        guild_id = request.args.get('guild_id') or request.json.get('guild_id') if request.json else None
        
        if not guild_id:
            return jsonify({'error': 'Sunucu ID gerekli'}), 400
        
        from database import Database
        db = Database()
        user_manager = UserManager(db)
        
        # Admin ise tüm sunuculara erişebilir
        if user_manager.is_global_admin(request.current_user['discord_id']):
            db.close()
            return f(*args, **kwargs)
        
        # Normal kullanıcı için sunucu erişimi kontrol et
        has_access = user_manager.has_guild_access(request.current_user['user_id'], guild_id)
        db.close()
        
        if not has_access:
            return jsonify({'error': 'Bu sunucuya erişim yetkiniz yok'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function