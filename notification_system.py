"""
Gelişmiş bildirim sistemi
Fiyat hedefleri, özel uyarılar ve bildirim yönetimi
"""
import sqlite3
from datetime import datetime, timedelta
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    PRICE_DROP = "price_drop"
    PRICE_TARGET = "price_target"
    STOCK_ALERT = "stock_alert"
    DAILY_SUMMARY = "daily_summary"

class NotificationSystem:
    def __init__(self, database):
        self.db = database
        self.create_notification_tables()
    
    def create_notification_tables(self):
        """Bildirim tabloları oluştur"""
        try:
            self.db.cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT,
                    user_id TEXT,
                    guild_id TEXT,
                    channel_id TEXT,
                    target_price REAL,
                    condition TEXT, -- 'below', 'above', 'exact'
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP,
                    triggered_at TIMESTAMP,
                    FOREIGN KEY(product_id) REFERENCES products(product_id)
                )
            ''')
            
            self.db.cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    guild_id TEXT,
                    notification_type TEXT,
                    is_enabled BOOLEAN DEFAULT 1,
                    settings TEXT, -- JSON format
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            self.db.cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    guild_id TEXT,
                    product_id TEXT,
                    notification_type TEXT,
                    message TEXT,
                    sent_at TIMESTAMP,
                    is_read BOOLEAN DEFAULT 0
                )
            ''')
            
            self.db.conn.commit()
            logger.info("Bildirim tabloları oluşturuldu")
            
        except Exception as e:
            logger.error(f"Bildirim tabloları oluşturulurken hata: {e}")
    
    def add_price_target(self, product_id, user_id, guild_id, channel_id, target_price, condition='below'):
        """Fiyat hedefi ekle"""
        try:
            # Mevcut aktif hedefi kontrol et
            existing = self.db.cursor.execute('''
                SELECT id FROM price_targets 
                WHERE product_id = ? AND user_id = ? AND guild_id = ? 
                AND is_active = 1 AND condition = ?
            ''', (product_id, user_id, guild_id, condition)).fetchone()
            
            if existing:
                # Mevcut hedefi güncelle
                self.db.cursor.execute('''
                    UPDATE price_targets 
                    SET target_price = ?, updated_at = ?
                    WHERE id = ?
                ''', (target_price, datetime.now().isoformat(), existing[0]))
                logger.info(f"Fiyat hedefi güncellendi: {product_id} -> ₺{target_price}")
            else:
                # Yeni hedef ekle
                self.db.cursor.execute('''
                    INSERT INTO price_targets 
                    (product_id, user_id, guild_id, channel_id, target_price, condition, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (product_id, user_id, guild_id, channel_id, target_price, condition, datetime.now().isoformat()))
                logger.info(f"Yeni fiyat hedefi eklendi: {product_id} -> ₺{target_price}")
            
            self.db.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Fiyat hedefi eklenirken hata: {e}")
            return False
    
    def check_price_targets(self, product_id, current_price):
        """Fiyat hedeflerini kontrol et ve tetiklenen bildirimleri döndür"""
        try:
            # Aktif fiyat hedeflerini getir
            self.db.cursor.execute('''
                SELECT pt.*, p.name, p.url, p.image_url
                FROM price_targets pt
                JOIN products p ON pt.product_id = p.product_id
                WHERE pt.product_id = ? AND pt.is_active = 1
            ''', (product_id,))
            
            targets = self.db.cursor.fetchall()
            triggered_notifications = []
            
            for target in targets:
                target_id, product_id, user_id, guild_id, channel_id, target_price, condition, is_active, created_at, triggered_at, name, url, image_url = target
                
                should_trigger = False
                
                if condition == 'below' and current_price <= target_price:
                    should_trigger = True
                elif condition == 'above' and current_price >= target_price:
                    should_trigger = True
                elif condition == 'exact' and abs(current_price - target_price) <= 0.01:
                    should_trigger = True
                
                if should_trigger:
                    # Hedefi tetiklenmiş olarak işaretle
                    self.db.cursor.execute('''
                        UPDATE price_targets 
                        SET is_active = 0, triggered_at = ?
                        WHERE id = ?
                    ''', (datetime.now().isoformat(), target_id))
                    
                    # Bildirim geçmişine ekle
                    message = f"Fiyat hedefi gerçekleşti! {name} ürünü ₺{target_price} {condition} hedefine ulaştı. Mevcut fiyat: ₺{current_price}"
                    self.add_notification_history(user_id, guild_id, product_id, NotificationType.PRICE_TARGET.value, message)
                    
                    triggered_notifications.append({
                        'user_id': user_id,
                        'guild_id': guild_id,
                        'channel_id': channel_id,
                        'product_id': product_id,
                        'product_name': name,
                        'product_url': url,
                        'product_image': image_url,
                        'target_price': target_price,
                        'current_price': current_price,
                        'condition': condition,
                        'message': message
                    })
            
            self.db.conn.commit()
            return triggered_notifications
            
        except Exception as e:
            logger.error(f"Fiyat hedefleri kontrol edilirken hata: {e}")
            return []
    
    def get_user_price_targets(self, user_id, guild_id=None):
        """Kullanıcının fiyat hedeflerini getir"""
        try:
            query = '''
                SELECT pt.*, p.name, p.current_price, p.url
                FROM price_targets pt
                JOIN products p ON pt.product_id = p.product_id
                WHERE pt.user_id = ? AND pt.is_active = 1
            '''
            params = [user_id]
            
            if guild_id:
                query += ' AND pt.guild_id = ?'
                params.append(guild_id)
            
            query += ' ORDER BY pt.created_at DESC'
            
            self.db.cursor.execute(query, params)
            results = self.db.cursor.fetchall()
            
            targets = []
            for row in results:
                targets.append({
                    'id': row[0],
                    'product_id': row[1],
                    'target_price': row[5],
                    'condition': row[6],
                    'created_at': row[8],
                    'product_name': row[10],
                    'current_price': row[11],
                    'product_url': row[12]
                })
            
            return targets
            
        except Exception as e:
            logger.error(f"Kullanıcı fiyat hedefleri getirilirken hata: {e}")
            return []
    
    def remove_price_target(self, target_id, user_id):
        """Fiyat hedefini kaldır"""
        try:
            self.db.cursor.execute('''
                UPDATE price_targets 
                SET is_active = 0 
                WHERE id = ? AND user_id = ?
            ''', (target_id, user_id))
            
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Fiyat hedefi kaldırılırken hata: {e}")
            return False
    
    def add_notification_history(self, user_id, guild_id, product_id, notification_type, message):
        """Bildirim geçmişine ekle"""
        try:
            self.db.cursor.execute('''
                INSERT INTO notification_history 
                (user_id, guild_id, product_id, notification_type, message, sent_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, guild_id, product_id, notification_type, message, datetime.now().isoformat()))
            
            self.db.conn.commit()
            
        except Exception as e:
            logger.error(f"Bildirim geçmişi eklenirken hata: {e}")
    
    def get_notification_history(self, user_id, guild_id=None, limit=20):
        """Kullanıcının bildirim geçmişini getir"""
        try:
            query = '''
                SELECT nh.*, p.name as product_name, p.url as product_url
                FROM notification_history nh
                LEFT JOIN products p ON nh.product_id = p.product_id
                WHERE nh.user_id = ?
            '''
            params = [user_id]
            
            if guild_id:
                query += ' AND nh.guild_id = ?'
                params.append(guild_id)
            
            query += ' ORDER BY nh.sent_at DESC LIMIT ?'
            params.append(limit)
            
            self.db.cursor.execute(query, params)
            results = self.db.cursor.fetchall()
            
            notifications = []
            for row in results:
                notifications.append({
                    'id': row[0],
                    'product_id': row[2],
                    'notification_type': row[3],
                    'message': row[4],
                    'sent_at': row[5],
                    'is_read': bool(row[6]),
                    'product_name': row[7],
                    'product_url': row[8]
                })
            
            return notifications
            
        except Exception as e:
            logger.error(f"Bildirim geçmişi getirilirken hata: {e}")
            return []
    
    def mark_notifications_read(self, user_id, notification_ids=None):
        """Bildirimleri okundu olarak işaretle"""
        try:
            if notification_ids:
                # Belirli bildirimleri işaretle
                placeholders = ','.join(['?' for _ in notification_ids])
                query = f'UPDATE notification_history SET is_read = 1 WHERE user_id = ? AND id IN ({placeholders})'
                params = [user_id] + notification_ids
            else:
                # Tüm bildirimleri işaretle
                query = 'UPDATE notification_history SET is_read = 1 WHERE user_id = ?'
                params = [user_id]
            
            self.db.cursor.execute(query, params)
            self.db.conn.commit()
            
            return self.db.cursor.rowcount
            
        except Exception as e:
            logger.error(f"Bildirimler okundu işaretlenirken hata: {e}")
            return 0
    
    def get_daily_summary(self, guild_id):
        """Günlük özet bilgilerini getir"""
        try:
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # Bugün eklenen ürünler
            self.db.cursor.execute('''
                SELECT COUNT(*) FROM products 
                WHERE guild_id = ? AND DATE(added_at) = ?
            ''', (guild_id, today.isoformat()))
            products_added_today = self.db.cursor.fetchone()[0]
            
            # Dün fiyat değişen ürünler
            self.db.cursor.execute('''
                SELECT COUNT(DISTINCT product_id) FROM price_history 
                WHERE DATE(date) = ?
            ''', (yesterday.isoformat(),))
            price_changes_yesterday = self.db.cursor.fetchone()[0]
            
            # En çok düşen fiyatlar (dün)
            self.db.cursor.execute('''
                SELECT p.name, p.current_price, 
                       (SELECT price FROM price_history ph 
                        WHERE ph.product_id = p.product_id 
                        AND DATE(ph.date) = ? 
                        ORDER BY ph.date ASC LIMIT 1) as yesterday_price
                FROM products p
                WHERE p.guild_id = ? AND p.current_price IS NOT NULL
                AND (SELECT price FROM price_history ph 
                     WHERE ph.product_id = p.product_id 
                     AND DATE(ph.date) = ? 
                     ORDER BY ph.date ASC LIMIT 1) IS NOT NULL
                AND p.current_price < (SELECT price FROM price_history ph 
                                      WHERE ph.product_id = p.product_id 
                                      AND DATE(ph.date) = ? 
                                      ORDER BY ph.date ASC LIMIT 1)
                ORDER BY ((SELECT price FROM price_history ph 
                          WHERE ph.product_id = p.product_id 
                          AND DATE(ph.date) = ? 
                          ORDER BY ph.date ASC LIMIT 1) - p.current_price) DESC
                LIMIT 5
            ''', (yesterday.isoformat(), guild_id, yesterday.isoformat(), yesterday.isoformat(), yesterday.isoformat()))
            
            biggest_drops = []
            for row in self.db.cursor.fetchall():
                if row[2]:  # yesterday_price exists
                    drop_amount = row[2] - row[1]
                    drop_percentage = (drop_amount / row[2]) * 100
                    biggest_drops.append({
                        'name': row[0],
                        'current_price': row[1],
                        'yesterday_price': row[2],
                        'drop_amount': drop_amount,
                        'drop_percentage': drop_percentage
                    })
            
            return {
                'date': today.isoformat(),
                'products_added_today': products_added_today,
                'price_changes_yesterday': price_changes_yesterday,
                'biggest_drops': biggest_drops
            }
            
        except Exception as e:
            logger.error(f"Günlük özet getirilirken hata: {e}")
            return None
    
    def cleanup_old_notifications(self, days=30):
        """Eski bildirimleri temizle"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            self.db.cursor.execute('''
                DELETE FROM notification_history 
                WHERE sent_at < ? AND is_read = 1
            ''', (cutoff_date,))
            
            deleted_count = self.db.cursor.rowcount
            self.db.conn.commit()
            
            logger.info(f"{deleted_count} eski bildirim temizlendi")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Eski bildirimler temizlenirken hata: {e}")
            return 0