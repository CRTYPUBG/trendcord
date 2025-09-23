#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kullanıcı Bazlı Veritabanı Sistemi
Her kullanıcının kendi verilerini yönetebileceği izole sistem
"""

import sqlite3
import json
import os
import logging
from datetime import datetime
from user_auth import UserEncryption

logger = logging.getLogger(__name__)

class UserDatabase:
    """Kullanıcı bazlı veritabanı yönetimi"""
    
    def __init__(self, db_name="data/trendyol_tracker.sqlite"):
        self.db_name = db_name
        self.encryption = UserEncryption()
        
        try:
            os.makedirs(os.path.dirname(db_name), exist_ok=True)
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self._create_user_tables()
            logger.info(f"Kullanıcı veritabanı bağlantısı kuruldu: {db_name}")
        except Exception as e:
            logger.error(f"Kullanıcı veritabanı bağlantısı hatası: {e}")
            raise
    
    def _create_user_tables(self):
        """Kullanıcı bazlı tabloları oluştur"""
        try:
            # Kullanıcı ürünleri tablosu (şifrelenmiş)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                encrypted_data TEXT NOT NULL,
                guild_id TEXT,
                channel_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, product_id, guild_id)
            )
            ''')
            
            # Kullanıcı fiyat geçmişi (şifrelenmiş)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                encrypted_price_data TEXT NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Kullanıcı bildirimleri (şifrelenmiş)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                encrypted_notification_data TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Kullanıcı fiyat hedefleri (şifrelenmiş)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_price_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                encrypted_target_data TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                triggered_at TIMESTAMP NULL
            )
            ''')
            
            # Kullanıcı ayarları (şifrelenmiş)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                encrypted_settings TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            self.conn.commit()
            logger.info("Kullanıcı tabloları oluşturuldu")
            
        except Exception as e:
            logger.error(f"Kullanıcı tabloları oluşturma hatası: {e}")
    
    def _get_user_encryption_key(self, user_id, encryption_key_hash):
        """Kullanıcının şifreleme anahtarını al"""
        try:
            return self.encryption.generate_user_key(str(user_id), encryption_key_hash)
        except Exception as e:
            logger.error(f"Kullanıcı şifreleme anahtarı alma hatası: {e}")
            return None
    
    def add_user_product(self, user_id, encryption_key_hash, product_data, guild_id, channel_id):
        """Kullanıcıya ürün ekle (şifrelenmiş)"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return False
            
            # Ürün verilerini şifrele
            encrypted_data = self.encryption.encrypt_data(product_data, user_key)
            if not encrypted_data:
                return False
            
            # Aynı ürün var mı kontrol et
            existing = self.cursor.execute('''
            SELECT id FROM user_products 
            WHERE user_id = ? AND product_id = ? AND guild_id = ?
            ''', (user_id, product_data['product_id'], guild_id)).fetchone()
            
            if existing:
                logger.warning(f"Kullanıcı ürünü zaten mevcut: {product_data['product_id']}")
                return False
            
            # Ürünü ekle
            self.cursor.execute('''
            INSERT INTO user_products 
            (user_id, product_id, encrypted_data, guild_id, channel_id)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, product_data['product_id'], encrypted_data, guild_id, channel_id))
            
            # İlk fiyat kaydını ekle
            if product_data.get('current_price') is not None:
                self.add_user_price_history(user_id, encryption_key_hash, 
                                          product_data['product_id'], 
                                          product_data['current_price'])
            
            self.conn.commit()
            logger.info(f"Kullanıcı ürünü eklendi: {user_id} - {product_data['product_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Kullanıcı ürünü ekleme hatası: {e}")
            self.conn.rollback()
            return False
    
    def get_user_products(self, user_id, encryption_key_hash, guild_id=None):
        """Kullanıcının ürünlerini al (şifreli verileri çöz)"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return []
            
            # Sorgu oluştur
            if guild_id:
                query = '''
                SELECT product_id, encrypted_data, guild_id, channel_id, created_at, updated_at
                FROM user_products 
                WHERE user_id = ? AND guild_id = ?
                ORDER BY created_at DESC
                '''
                params = (user_id, guild_id)
            else:
                query = '''
                SELECT product_id, encrypted_data, guild_id, channel_id, created_at, updated_at
                FROM user_products 
                WHERE user_id = ?
                ORDER BY created_at DESC
                '''
                params = (user_id,)
            
            results = self.cursor.execute(query, params).fetchall()
            
            products = []
            for row in results:
                try:
                    # Şifrelenmiş veriyi çöz
                    decrypted_data = self.encryption.decrypt_data(row[1], user_key)
                    if decrypted_data:
                        product_data = json.loads(decrypted_data)
                        product_data.update({
                            'guild_id': row[2],
                            'channel_id': row[3],
                            'created_at': row[4],
                            'updated_at': row[5]
                        })
                        products.append(product_data)
                except Exception as e:
                    logger.error(f"Ürün verisi çözme hatası: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Kullanıcı ürünleri alma hatası: {e}")
            return []
    
    def update_user_product_price(self, user_id, encryption_key_hash, product_id, new_price):
        """Kullanıcı ürün fiyatını güncelle"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return False
            
            # Mevcut ürün verisini al
            result = self.cursor.execute('''
            SELECT encrypted_data FROM user_products 
            WHERE user_id = ? AND product_id = ?
            ''', (user_id, product_id)).fetchone()
            
            if not result:
                return False
            
            # Veriyi çöz ve güncelle
            decrypted_data = self.encryption.decrypt_data(result[0], user_key)
            if not decrypted_data:
                return False
            
            product_data = json.loads(decrypted_data)
            product_data['current_price'] = new_price
            product_data['last_checked'] = datetime.now().isoformat()
            
            # Yeniden şifrele
            encrypted_data = self.encryption.encrypt_data(product_data, user_key)
            if not encrypted_data:
                return False
            
            # Veritabanını güncelle
            self.cursor.execute('''
            UPDATE user_products 
            SET encrypted_data = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND product_id = ?
            ''', (encrypted_data, user_id, product_id))
            
            # Fiyat geçmişine ekle
            self.add_user_price_history(user_id, encryption_key_hash, product_id, new_price)
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Kullanıcı ürün fiyatı güncelleme hatası: {e}")
            self.conn.rollback()
            return False
    
    def add_user_price_history(self, user_id, encryption_key_hash, product_id, price):
        """Kullanıcı fiyat geçmişi ekle"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return False
            
            price_data = {
                'price': price,
                'date': datetime.now().isoformat()
            }
            
            encrypted_price_data = self.encryption.encrypt_data(price_data, user_key)
            if not encrypted_price_data:
                return False
            
            self.cursor.execute('''
            INSERT INTO user_price_history 
            (user_id, product_id, encrypted_price_data)
            VALUES (?, ?, ?)
            ''', (user_id, product_id, encrypted_price_data))
            
            return True
            
        except Exception as e:
            logger.error(f"Kullanıcı fiyat geçmişi ekleme hatası: {e}")
            return False
    
    def get_user_price_history(self, user_id, encryption_key_hash, product_id, limit=10):
        """Kullanıcı fiyat geçmişini al"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return []
            
            results = self.cursor.execute('''
            SELECT encrypted_price_data, date FROM user_price_history 
            WHERE user_id = ? AND product_id = ?
            ORDER BY date DESC LIMIT ?
            ''', (user_id, product_id, limit)).fetchall()
            
            history = []
            for row in results:
                try:
                    decrypted_data = self.encryption.decrypt_data(row[0], user_key)
                    if decrypted_data:
                        price_data = json.loads(decrypted_data)
                        history.append(price_data)
                except Exception as e:
                    logger.error(f"Fiyat geçmişi çözme hatası: {e}")
                    continue
            
            return history
            
        except Exception as e:
            logger.error(f"Kullanıcı fiyat geçmişi alma hatası: {e}")
            return []
    
    def delete_user_product(self, user_id, product_id, guild_id=None):
        """Kullanıcı ürünü sil"""
        try:
            if guild_id:
                # Belirli sunucudan sil
                self.cursor.execute('''
                DELETE FROM user_products 
                WHERE user_id = ? AND product_id = ? AND guild_id = ?
                ''', (user_id, product_id, guild_id))
            else:
                # Tüm sunuculardan sil
                self.cursor.execute('''
                DELETE FROM user_products 
                WHERE user_id = ? AND product_id = ?
                ''', (user_id, product_id))
            
            deleted_rows = self.cursor.rowcount
            
            if deleted_rows > 0:
                # İlişkili fiyat geçmişini sil
                self.cursor.execute('''
                DELETE FROM user_price_history 
                WHERE user_id = ? AND product_id = ?
                ''', (user_id, product_id))
                
                self.conn.commit()
                logger.info(f"Kullanıcı ürünü silindi: {user_id} - {product_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Kullanıcı ürünü silme hatası: {e}")
            self.conn.rollback()
            return False
    
    def add_user_notification(self, user_id, encryption_key_hash, notification_data):
        """Kullanıcı bildirimi ekle"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return False
            
            encrypted_data = self.encryption.encrypt_data(notification_data, user_key)
            if not encrypted_data:
                return False
            
            self.cursor.execute('''
            INSERT INTO user_notifications 
            (user_id, encrypted_notification_data)
            VALUES (?, ?)
            ''', (user_id, encrypted_data))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Kullanıcı bildirimi ekleme hatası: {e}")
            return False
    
    def get_user_notifications(self, user_id, encryption_key_hash, unread_only=False, limit=50):
        """Kullanıcı bildirimlerini al"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return []
            
            query = '''
            SELECT id, encrypted_notification_data, is_read, created_at
            FROM user_notifications 
            WHERE user_id = ?
            '''
            params = [user_id]
            
            if unread_only:
                query += ' AND is_read = 0'
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            results = self.cursor.execute(query, params).fetchall()
            
            notifications = []
            for row in results:
                try:
                    decrypted_data = self.encryption.decrypt_data(row[1], user_key)
                    if decrypted_data:
                        notification_data = json.loads(decrypted_data)
                        notification_data.update({
                            'id': row[0],
                            'is_read': bool(row[2]),
                            'created_at': row[3]
                        })
                        notifications.append(notification_data)
                except Exception as e:
                    logger.error(f"Bildirim verisi çözme hatası: {e}")
                    continue
            
            return notifications
            
        except Exception as e:
            logger.error(f"Kullanıcı bildirimleri alma hatası: {e}")
            return []
    
    def mark_user_notifications_read(self, user_id, notification_ids=None):
        """Kullanıcı bildirimlerini okundu işaretle"""
        try:
            if notification_ids:
                # Belirli bildirimleri işaretle
                placeholders = ','.join(['?' for _ in notification_ids])
                query = f'''
                UPDATE user_notifications 
                SET is_read = 1 
                WHERE user_id = ? AND id IN ({placeholders})
                '''
                params = [user_id] + notification_ids
            else:
                # Tüm bildirimleri işaretle
                query = 'UPDATE user_notifications SET is_read = 1 WHERE user_id = ?'
                params = [user_id]
            
            self.cursor.execute(query, params)
            marked_count = self.cursor.rowcount
            self.conn.commit()
            
            return marked_count
            
        except Exception as e:
            logger.error(f"Bildirim işaretleme hatası: {e}")
            return 0
    
    def add_user_price_target(self, user_id, encryption_key_hash, target_data):
        """Kullanıcı fiyat hedefi ekle"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return False
            
            encrypted_data = self.encryption.encrypt_data(target_data, user_key)
            if not encrypted_data:
                return False
            
            self.cursor.execute('''
            INSERT INTO user_price_targets 
            (user_id, product_id, encrypted_target_data)
            VALUES (?, ?, ?)
            ''', (user_id, target_data['product_id'], encrypted_data))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Kullanıcı fiyat hedefi ekleme hatası: {e}")
            return False
    
    def get_user_price_targets(self, user_id, encryption_key_hash, active_only=True):
        """Kullanıcı fiyat hedeflerini al"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return []
            
            query = '''
            SELECT id, product_id, encrypted_target_data, is_active, created_at, triggered_at
            FROM user_price_targets 
            WHERE user_id = ?
            '''
            params = [user_id]
            
            if active_only:
                query += ' AND is_active = 1'
            
            query += ' ORDER BY created_at DESC'
            
            results = self.cursor.execute(query, params).fetchall()
            
            targets = []
            for row in results:
                try:
                    decrypted_data = self.encryption.decrypt_data(row[2], user_key)
                    if decrypted_data:
                        target_data = json.loads(decrypted_data)
                        target_data.update({
                            'id': row[0],
                            'is_active': bool(row[3]),
                            'created_at': row[4],
                            'triggered_at': row[5]
                        })
                        targets.append(target_data)
                except Exception as e:
                    logger.error(f"Fiyat hedefi verisi çözme hatası: {e}")
                    continue
            
            return targets
            
        except Exception as e:
            logger.error(f"Kullanıcı fiyat hedefleri alma hatası: {e}")
            return []
    
    def update_user_settings(self, user_id, encryption_key_hash, settings_data):
        """Kullanıcı ayarlarını güncelle"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return False
            
            encrypted_data = self.encryption.encrypt_data(settings_data, user_key)
            if not encrypted_data:
                return False
            
            # Mevcut ayar var mı kontrol et
            existing = self.cursor.execute(
                'SELECT id FROM user_settings WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            
            if existing:
                # Güncelle
                self.cursor.execute('''
                UPDATE user_settings 
                SET encrypted_settings = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                ''', (encrypted_data, user_id))
            else:
                # Yeni ekle
                self.cursor.execute('''
                INSERT INTO user_settings 
                (user_id, encrypted_settings)
                VALUES (?, ?)
                ''', (user_id, encrypted_data))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Kullanıcı ayarları güncelleme hatası: {e}")
            return False
    
    def get_user_settings(self, user_id, encryption_key_hash):
        """Kullanıcı ayarlarını al"""
        try:
            user_key = self._get_user_encryption_key(user_id, encryption_key_hash)
            if not user_key:
                return {}
            
            result = self.cursor.execute('''
            SELECT encrypted_settings FROM user_settings 
            WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            if result:
                decrypted_data = self.encryption.decrypt_data(result[0], user_key)
                if decrypted_data:
                    return json.loads(decrypted_data)
            
            # Varsayılan ayarlar
            return {
                'notifications_enabled': True,
                'price_check_interval': 3600,
                'theme': 'light',
                'language': 'tr',
                'email_notifications': False,
                'discord_notifications': True
            }
            
        except Exception as e:
            logger.error(f"Kullanıcı ayarları alma hatası: {e}")
            return {}
    
    def get_user_stats(self, user_id):
        """Kullanıcı istatistiklerini al (şifrelenmemiş)"""
        try:
            # Toplam ürün sayısı
            total_products = self.cursor.execute(
                'SELECT COUNT(*) FROM user_products WHERE user_id = ?',
                (user_id,)
            ).fetchone()[0]
            
            # Aktif fiyat hedefleri
            active_targets = self.cursor.execute(
                'SELECT COUNT(*) FROM user_price_targets WHERE user_id = ? AND is_active = 1',
                (user_id,)
            ).fetchone()[0]
            
            # Okunmamış bildirimler
            unread_notifications = self.cursor.execute(
                'SELECT COUNT(*) FROM user_notifications WHERE user_id = ? AND is_read = 0',
                (user_id,)
            ).fetchone()[0]
            
            # Sunucu sayısı
            guild_count = self.cursor.execute('''
            SELECT COUNT(DISTINCT guild_id) FROM user_products 
            WHERE user_id = ? AND guild_id IS NOT NULL
            ''', (user_id,)).fetchone()[0]
            
            return {
                'total_products': total_products,
                'active_targets': active_targets,
                'unread_notifications': unread_notifications,
                'guild_count': guild_count
            }
            
        except Exception as e:
            logger.error(f"Kullanıcı istatistikleri alma hatası: {e}")
            return {}
    
    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.conn:
            self.conn.close()