import sqlite3
import os
from datetime import datetime

def connect_db(db_path):
    """Veritabanına bağlan."""
    try:
        # Veritabanı dizini yoksa oluştur
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")  # Foreign key desteğini etkinleştir
        return conn
    except sqlite3.Error as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

def close_db(conn):
    """Veritabanı bağlantısını kapat."""
    if conn:
        conn.close()

def create_tables(db_path):
    """Gerekli veritabanı tablolarını oluştur."""
    conn = connect_db(db_path)
    if conn is not None:
        try:
            cursor = conn.cursor()
            # products tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trendyol_id TEXT UNIQUE NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    name TEXT,
                    image_url TEXT,
                    last_price REAL,
                    last_updated DATETIME,
                    is_available BOOLEAN
                )
            """)
            # tracked_products tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracked_products (
                    guild_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    tracking_channel_id INTEGER,
                    PRIMARY KEY (guild_id, product_id),
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)
            # price_history tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            print("Veritabanı tabloları kontrol edildi/oluşturuldu.")
        except sqlite3.Error as e:
            print(f"Tablo oluşturma hatası: {e}")
        finally:
            close_db(conn)
    else:
        print("Veritabanı bağlantısı kurulamadığı için tablolar oluşturulamadı.")

def add_product(conn, trendyol_id, url, name, image_url, last_price):
    """Ürünü ekler veya günceller, ürün ID'sini döndürür."""
    sql = """
        INSERT INTO products (trendyol_id, url, name, image_url, last_price, last_updated, is_available)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(trendyol_id) DO UPDATE SET
            url=excluded.url,
            name=excluded.name,
            image_url=excluded.image_url,
            last_price=excluded.last_price,
            last_updated=excluded.last_updated,
            is_available=excluded.is_available
        RETURNING id;
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    is_available = True  # Varsayılan olarak stokta kabul edelim
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (trendyol_id, url, name, image_url, last_price, current_time, is_available))
        product_id = cursor.fetchone()[0]
        conn.commit()
        return product_id
    except sqlite3.Error as e:
        print(f"Ürün ekleme/güncelleme hatası: {e}")
        conn.rollback()
        return None

def track_product(conn, guild_id, product_id, tracking_channel_id):
    """Bir sunucu için bir ürünü takip listesine ekler."""
    sql = """
        INSERT OR REPLACE INTO tracked_products (guild_id, product_id, tracking_channel_id)
        VALUES (?, ?, ?)
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (guild_id, product_id, tracking_channel_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ürün takip ekleme hatası: {e}")
        conn.rollback()
        return False

def untrack_product(conn, guild_id, product_id):
    """Bir sunucu için bir ürünü takip listesinden siler."""
    sql = """
        DELETE FROM tracked_products
        WHERE guild_id = ? AND product_id = ?
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (guild_id, product_id))
        conn.commit()
        return cursor.rowcount > 0  # True döner, eğer bir satır silindiyse
    except sqlite3.Error as e:
        print(f"Ürün takipten çıkarma hatası: {e}")
        conn.rollback()
        return False

def get_product_by_url(conn, url):
    """URL'ye göre ürün bilgilerini döndürür."""
    sql = """
        SELECT p.*, tp.guild_id, tp.tracking_channel_id
        FROM products p
        LEFT JOIN tracked_products tp ON p.id = tp.product_id
        WHERE p.url = ?
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (url,))
        row = cursor.fetchone()
        if row:
            col_names = [desc[0] for desc in cursor.description]
            return dict(zip(col_names, row))
        return None
    except sqlite3.Error as e:
        print(f"Ürün sorgulama hatası: {e}")
        return None

def get_product_by_id(conn, product_id):
    """ID'ye göre ürün bilgilerini döndürür."""
    sql = """
        SELECT p.*, tp.guild_id, tp.tracking_channel_id
        FROM products p
        LEFT JOIN tracked_products tp ON p.id = tp.product_id
        WHERE p.id = ?
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (product_id,))
        row = cursor.fetchone()
        if row:
            col_names = [desc[0] for desc in cursor.description]
            return dict(zip(col_names, row))
        return None
    except sqlite3.Error as e:
        print(f"Ürün sorgulama hatası: {e}")
        return None

def get_tracked_products_by_guild(conn, guild_id):
    """Bir sunucunun takip ettiği tüm ürünleri döndürür."""
    sql = """
        SELECT p.*, tp.guild_id, tp.tracking_channel_id
        FROM products p
        INNER JOIN tracked_products tp ON p.id = tp.product_id
        WHERE tp.guild_id = ?
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (guild_id,))
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        return [dict(zip(col_names, row)) for row in rows]
    except sqlite3.Error as e:
        print(f"Takip edilen ürünleri sorgulama hatası: {e}")
        return []

def get_all_tracked_products(conn):
    """Takip edilen tüm ürünleri döndürür."""
    sql = """
        SELECT p.id as product_id, p.trendyol_id, p.url, p.name, p.last_price, p.image_url,
               tp.guild_id, tp.tracking_channel_id
        FROM products p
        INNER JOIN tracked_products tp ON p.id = tp.product_id
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        return [dict(zip(col_names, row)) for row in rows]
    except sqlite3.Error as e:
        print(f"Takip edilen ürünleri sorgulama hatası: {e}")
        return []

def add_price_history(conn, product_id, price):
    """Ürün fiyat geçmişi ekler."""
    sql = """
        INSERT INTO price_history (product_id, price, timestamp)
        VALUES (?, ?, ?)
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (product_id, price, current_time))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Fiyat geçmişi ekleme hatası: {e}")
        conn.rollback()
        return False

def update_product_price(conn, product_id, new_price):
    """Ürün fiyatını günceller ve geçmişe ekler."""
    sql = """
        UPDATE products
        SET last_price = ?, last_updated = ?
        WHERE id = ?
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (new_price, current_time, product_id))
        
        # Fiyat geçmişine de ekle
        add_price_history(conn, product_id, new_price)
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ürün fiyatı güncelleme hatası: {e}")
        conn.rollback()
        return False 