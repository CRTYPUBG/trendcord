import sqlite3
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name="data/trendyol_tracker.sqlite"):
        """Veritabanı bağlantısını başlatır ve tabloları oluşturur."""
        self.db_name = db_name
        
        try:
            # Eğer data klasörü yoksa oluştur
            os.makedirs(os.path.dirname(db_name), exist_ok=True)
            
            # Tam dosya yolunu al
            abs_path = os.path.abspath(db_name)
            logger.info(f"Veritabanı dosyası yolu: {abs_path}")
            
            # Klasör yazılabilir mi?
            if os.access(os.path.dirname(abs_path), os.W_OK):
                logger.info(f"Klasöre yazma izni var: {os.path.dirname(abs_path)}")
            else:
                logger.error(f"HATA: Klasöre yazma izni yok: {os.path.dirname(abs_path)}")
            
            # Veritabanı bağlantısı oluştur
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.create_tables()
            logger.info(f"Veritabanı bağlantısı başarıyla kuruldu: {db_name}")
        except Exception as e:
            logger.error(f"Veritabanı bağlantısı oluşturulurken hata: {e}")
            logger.error(f"Veritabanı dosyası: {db_name}")
            raise

    def create_tables(self):
        """Gerekli tabloları oluşturur."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT UNIQUE,
            name TEXT,
            url TEXT,
            image_url TEXT,
            current_price REAL,
            original_price REAL,
            added_at TIMESTAMP,
            last_checked TIMESTAMP,
            guild_id TEXT,
            user_id TEXT,
            channel_id TEXT
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            price REAL,
            date TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
        ''')
        
        self.conn.commit()

    def add_product(self, product_data, guild_id, user_id, channel_id):
        """Ürün ekler ve ilk fiyat kaydını oluşturur."""
        try:
            # Veri doğrulama
            if not product_data.get('product_id'):
                logger.error("Ürün ID'si eksik")
                return False
                
            if not product_data.get('name'):
                logger.error("Ürün adı eksik")
                return False
                
            if product_data.get('current_price') is None:
                logger.error("Ürün fiyatı eksik")
                return False
            
            # Aynı ürünün bu sunucuda zaten var olup olmadığını kontrol et
            existing = self.cursor.execute('''
                SELECT id FROM products 
                WHERE product_id = ? AND guild_id = ?
            ''', (product_data['product_id'], guild_id)).fetchone()
            
            if existing:
                logger.warning(f"Ürün zaten bu sunucuda mevcut: {product_data['product_id']}")
                return False
            
            now = datetime.now().isoformat()
            
            # Ürünü ekleme
            self.cursor.execute('''
            INSERT INTO products 
            (product_id, name, url, image_url, current_price, original_price, added_at, last_checked, guild_id, user_id, channel_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data['product_id'],
                product_data['name'],
                product_data['url'],
                product_data.get('image_url'),
                product_data['current_price'],
                product_data.get('original_price', product_data['current_price']),
                now,
                now,
                guild_id,
                user_id,
                channel_id
            ))
            
            # Fiyat geçmişi kaydı ekleme
            if product_data['current_price'] is not None:
                self.cursor.execute('''
                INSERT INTO price_history 
                (product_id, price, date) 
                VALUES (?, ?, ?)
                ''', (
                    product_data['product_id'],
                    product_data['current_price'],
                    now
                ))
            
            self.conn.commit()
            logger.info(f"Ürün başarıyla eklendi: {product_data['name']} ({product_data['product_id']})")
            return True
            
        except sqlite3.IntegrityError as e:
            logger.warning(f"Ürün zaten mevcut: {product_data.get('product_id', 'Bilinmeyen')} - {e}")
            return False
        except Exception as e:
            logger.error(f"Ürün eklenirken hata: {e}")
            self.conn.rollback()
            return False

    def get_product(self, product_id):
        """Belirli bir ürünün bilgilerini getirir."""
        self.cursor.execute('''
        SELECT * FROM products WHERE product_id = ?
        ''', (product_id,))
        
        result = self.cursor.fetchone()
        if result:
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, result))
        return None

    def get_all_products(self, guild_id=None, user_id=None, is_admin=False):
        """
        Ürünleri getirir - sunucu bazlı izolasyon ile
        
        Args:
            guild_id: Sunucu ID'si
            user_id: Kullanıcı ID'si (opsiyonel)
            is_admin: Admin ise tüm ürünleri görebilir
        """
        if is_admin and not guild_id:
            # Admin ve guild_id belirtilmemişse tüm ürünleri getir
            query = "SELECT * FROM products ORDER BY added_at DESC"
            params = []
        elif guild_id:
            # Belirli sunucunun ürünlerini getir
            query = "SELECT * FROM products WHERE guild_id = ?"
            params = [guild_id]
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
                
            query += " ORDER BY added_at DESC"
        else:
            # Hiçbir şey belirtilmemişse boş liste döndür
            return []
        
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        products = []
        if results:
            columns = [desc[0] for desc in self.cursor.description]
            for row in results:
                products.append(dict(zip(columns, row)))
        
        return products
    
    def get_guild_product_count(self, guild_id):
        """Belirli bir sunucudaki ürün sayısını döndürür"""
        self.cursor.execute('SELECT COUNT(*) FROM products WHERE guild_id = ?', (guild_id,))
        return self.cursor.fetchone()[0]
    
    def get_all_guilds_stats(self):
        """Tüm sunucuların istatistiklerini döndürür (admin için)"""
        self.cursor.execute('''
        SELECT guild_id, COUNT(*) as product_count, 
               MIN(added_at) as first_product, 
               MAX(added_at) as last_product
        FROM products 
        GROUP BY guild_id 
        ORDER BY product_count DESC
        ''')
        
        results = self.cursor.fetchall()
        stats = []
        
        if results:
            for row in results:
                stats.append({
                    'guild_id': row[0],
                    'product_count': row[1],
                    'first_product': row[2],
                    'last_product': row[3]
                })
        
        return stats

    def update_product_price(self, product_id, new_price):
        """Ürün fiyatını günceller ve fiyat geçmişine ekler."""
        try:
            now = datetime.now().isoformat()
            
            logger.info(f"Ürün fiyatı güncelleniyor: {product_id} -> {new_price} TL")
            
            # Ürün fiyatını güncelleme
            self.cursor.execute('''
            UPDATE products 
            SET current_price = ?, last_checked = ? 
            WHERE product_id = ?
            ''', (new_price, now, product_id))
            
            update_row_count = self.cursor.rowcount
            logger.info(f"Güncellenen satır sayısı: {update_row_count}")
            
            # Fiyat geçmişi kaydı ekleme
            self.cursor.execute('''
            INSERT INTO price_history 
            (product_id, price, date) 
            VALUES (?, ?, ?)
            ''', (product_id, new_price, now))
            
            insert_row_count = self.cursor.rowcount
            logger.info(f"Eklenen fiyat geçmişi satır sayısı: {insert_row_count}")
            
            self.conn.commit()
            logger.info(f"İşlemler veritabanına kaydedildi (commit yapıldı)")
            return True
        except Exception as e:
            logger.error(f"Ürün fiyatı güncellenirken hata: {e}")
            self.conn.rollback()
            logger.error(f"İşlemler geri alındı (rollback yapıldı)")
            return False

    def get_price_history(self, product_id, limit=10):
        """Ürün fiyat geçmişini getirir."""
        self.cursor.execute('''
        SELECT price, date FROM price_history 
        WHERE product_id = ? 
        ORDER BY date DESC LIMIT ?
        ''', (product_id, limit))
        
        results = self.cursor.fetchall()
        history = []
        
        if results:
            for row in results:
                history.append({"price": row[0], "date": row[1]})
        
        return history

    def delete_product(self, product_id, guild_id=None, user_id=None):
        """Ürünü ve fiyat geçmişini siler."""
        try:
            # Önce ürünün var olup olmadığını kontrol et
            existing_product = self.get_product(product_id)
            if not existing_product:
                logger.warning(f"Silinmeye çalışılan ürün bulunamadı: {product_id}")
                return False
            
            # Silme koşullarını belirle
            if guild_id:
                # Guild bazlı silme (sadece belirli sunucudan)
                if user_id:
                    # Hem guild hem user kontrolü
                    self.cursor.execute('''
                    DELETE FROM products 
                    WHERE product_id = ? AND guild_id = ? AND user_id = ?
                    ''', (product_id, guild_id, user_id))
                else:
                    # Sadece guild kontrolü
                    self.cursor.execute('''
                    DELETE FROM products 
                    WHERE product_id = ? AND guild_id = ?
                    ''', (product_id, guild_id))
            else:
                # Tüm kayıtları sil (admin işlemi)
                self.cursor.execute('''
                DELETE FROM products 
                WHERE product_id = ?
                ''', (product_id,))
            
            deleted_rows = self.cursor.rowcount
            
            if deleted_rows > 0:
                # İlişkili fiyat geçmişini silme
                self.cursor.execute('''
                DELETE FROM price_history 
                WHERE product_id = ?
                ''', (product_id,))
                
                self.conn.commit()
                logger.info(f"Ürün başarıyla silindi: {product_id} ({deleted_rows} kayıt)")
                return True
            else:
                logger.warning(f"Silinecek ürün bulunamadı veya yetki yok: {product_id}")
                return False
                
        except Exception as e:
            logger.error(f"Ürün silinirken hata: {e}")
            self.conn.rollback()
            return False

    def check_price_changes(self):
        """Fiyat değişikliklerini kontrol eder ve değişen ürünleri döndürür."""
        self.cursor.execute('''
        SELECT p.*, 
            (SELECT price FROM price_history 
             WHERE product_id = p.product_id 
             ORDER BY date DESC LIMIT 1, 1) as previous_price
        FROM products p
        ''')
        
        results = self.cursor.fetchall()
        changed_products = []
        
        if results:
            columns = [desc[0] for desc in self.cursor.description]
            for row in results:
                product = dict(zip(columns, row))
                
                # Eğer önceki fiyat varsa ve farklıysa
                if product['previous_price'] and product['current_price'] != product['previous_price']:
                    product['price_change'] = product['current_price'] - product['previous_price']
                    product['price_change_percentage'] = (product['price_change'] / product['previous_price']) * 100
                    changed_products.append(product)
        
        return changed_products

    def close(self):
        """Veritabanı bağlantısını kapatır."""
        if self.conn:
            self.conn.close()
        
    def test_database(self):
        """Veritabanı bağlantısını ve işlemlerini test eder."""
        try:
            # Test verisi oluştur
            test_data = {
                'product_id': 'test123',
                'name': 'Test Ürün',
                'url': 'https://www.trendyol.com/test-urun-p-123456',
                'image_url': 'https://test.com/image.jpg',
                'current_price': 99.99,
                'original_price': 129.99,
                'success': True
            }
            
            # Test verisini ekle
            result = self.add_product(test_data, 'test_guild', 'test_user', 'test_channel')
            if result:
                logger.info("Veritabanı test verisi başarıyla eklendi.")
                
                # Eklenen veriyi kontrol et
                product = self.get_product('test123')
                if product:
                    logger.info(f"Test verisi başarıyla okundu: {product['name']}")
                    
                    # Test verisini sil
                    self.delete_product('test123')
                    logger.info("Test verisi silindi.")
                    return True
                else:
                    logger.error("Test verisi eklendi ancak okunamadı!")
            else:
                logger.error("Test verisi eklenemedi!")
            
            return False
        except Exception as e:
            logger.error(f"Veritabanı testi sırasında hata oluştu: {e}")
            return False 