#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trendyol Bot Web UI
Flask tabanlı web arayüzü
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import logging
from datetime import datetime, timedelta
import threading
import time
from database import Database
from scraper import TrendyolScraper
from trendyol_api import TrendyolAPI, TrendyolAPIFallback
from admin_utils import admin_manager
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Flask uygulaması
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'trendyol-bot-secret-key-2024')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global değişkenler
db = None
scraper = None
api_client = None
fallback = None
bot_status = {"running": False, "last_check": None, "total_products": 0}

def init_components():
    """Bot bileşenlerini başlat"""
    global scraper, api_client, fallback
    try:
        scraper = TrendyolScraper(use_proxy=False, verify_ssl=True)
        api_client = TrendyolAPI()
        fallback = TrendyolAPIFallback(api_client=api_client, scraper=scraper)
        logger.info("Web UI bileşenleri başarıyla başlatıldı")
        return True
    except Exception as e:
        logger.error(f"Web UI bileşenleri başlatılırken hata: {e}")
        return False

def get_db():
    """Thread-safe database connection"""
    return Database()

# Ana sayfa
@app.route('/')
def index():
    """Ana dashboard sayfası"""
    try:
        # Thread-safe database connection
        db = get_db()
        
        # İstatistikler
        stats = {
            'total_products': 0,
            'total_guilds': 0,
            'recent_products': [],
            'guild_stats': []
        }
        
        try:
            # Genel istatistikler
            all_stats = db.get_all_guilds_stats()
            stats['total_guilds'] = len(all_stats) if all_stats else 0
            stats['total_products'] = sum(stat['product_count'] for stat in all_stats) if all_stats else 0
            stats['guild_stats'] = all_stats[:10] if all_stats else []  # İlk 10 sunucu
            
            # Son eklenen ürünler
            recent_products = db.get_all_products(is_admin=True)
            stats['recent_products'] = recent_products[:10] if recent_products else []  # Son 10 ürün
        except Exception as e:
            logger.error(f"İstatistik hesaplama hatası: {e}")
            # Varsayılan değerler zaten ayarlandı
        
        db.close()
        
        # Admin sayısını güvenli şekilde al
        try:
            admin_count = len(admin_manager.get_global_admin_list())
        except Exception as e:
            logger.error(f"Admin sayısı alınırken hata: {e}")
            admin_count = 0
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             bot_status=bot_status,
                             admin_count=admin_count)
    except Exception as e:
        logger.error(f"Dashboard yüklenirken hata: {e}")
        return render_template('error.html', error=str(e))

# Ürünler sayfası
@app.route('/products')
def products():
    """Ürünler listesi sayfası"""
    try:
        db = get_db()
        
        guild_id = request.args.get('guild_id')
        page = int(request.args.get('page', 1))
        per_page = 20
        
        # Ürünleri getir
        all_products = db.get_all_products(guild_id=guild_id, is_admin=True)
        
        # Sayfalama
        start = (page - 1) * per_page
        end = start + per_page
        products = all_products[start:end]
        
        # Sayfa bilgileri
        total_pages = (len(all_products) + per_page - 1) // per_page
        
        # Sunucu listesi
        guild_stats = db.get_all_guilds_stats()
        
        db.close()
        
        return render_template('products.html', 
                             products=products,
                             guild_stats=guild_stats,
                             current_guild=guild_id,
                             page=page,
                             total_pages=total_pages,
                             total_products=len(all_products))
    except Exception as e:
        logger.error(f"Ürünler sayfası yüklenirken hata: {e}")
        return render_template('error.html', error=str(e))

# Ürün ekleme sayfası
@app.route('/add_product')
def add_product_page():
    """Ürün ekleme sayfası"""
    return render_template('add_product.html')

# API: Ürün ekleme
@app.route('/api/add_product', methods=['POST'])
def api_add_product():
    """API: Yeni ürün ekleme"""
    try:
        data = request.get_json()
        url = data.get('url')
        guild_id = data.get('guild_id', 'web_ui')
        user_id = data.get('user_id', 'web_admin')
        channel_id = data.get('channel_id', 'web_channel')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL gerekli'})
        
        if not fallback:
            init_components()
        
        # Ürün bilgilerini çek
        product_data = fallback.get_product_info(url)
        
        if not product_data or not product_data.get('success'):
            return jsonify({'success': False, 'error': 'Ürün bilgileri alınamadı'})
        
        # Veritabanına ekle
        db = get_db()
        success = db.add_product(product_data, guild_id, user_id, channel_id)
        db.close()
        
        if success:
            # WebSocket ile güncelleme gönder
            socketio.emit('product_added', {
                'product': product_data,
                'guild_id': guild_id
            })
            
            return jsonify({'success': True, 'product': product_data})
        else:
            return jsonify({'success': False, 'error': 'Ürün veritabanına eklenemedi'})
            
    except Exception as e:
        logger.error(f"Ürün ekleme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Ürün silme
@app.route('/api/delete_product', methods=['POST'])
def api_delete_product():
    """API: Ürün silme"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({'success': False, 'error': 'Ürün ID gerekli'})
        
        # Thread-safe database connection
        db = get_db()
        
        # Ürünü sil
        if db.delete_product(product_id):
            db.close()
            
            # WebSocket ile güncelleme gönder
            socketio.emit('product_deleted', {'product_id': product_id})
            
            return jsonify({'success': True})
        else:
            db.close()
            return jsonify({'success': False, 'error': 'Ürün silinemedi'})
            
    except Exception as e:
        logger.error(f"Ürün silme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Fiyat güncelleme
@app.route('/api/update_price', methods=['POST'])
def api_update_price():
    """API: Ürün fiyatı güncelleme"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        new_price = data.get('new_price')
        
        if not product_id or new_price is None:
            return jsonify({'success': False, 'error': 'Ürün ID ve yeni fiyat gerekli'})
        
        # Thread-safe database connection
        db = get_db()
        
        # Fiyatı güncelle
        if db.update_product_price(product_id, float(new_price)):
            db.close()
            
            # WebSocket ile güncelleme gönder
            socketio.emit('price_updated', {
                'product_id': product_id,
                'new_price': new_price
            })
            
            return jsonify({'success': True})
        else:
            db.close()
            return jsonify({'success': False, 'error': 'Fiyat güncellenemedi'})
            
    except Exception as e:
        logger.error(f"Fiyat güncelleme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: İstatistikler
@app.route('/api/stats')
def api_stats():
    """API: Genel istatistikler"""
    try:
        db = get_db()
        
        guild_stats = db.get_all_guilds_stats()
        total_products = sum(stat['product_count'] for stat in guild_stats)
        
        db.close()
        
        return jsonify({
            'success': True,
            'total_guilds': len(guild_stats),
            'total_products': total_products,
            'guild_stats': guild_stats,
            'bot_status': bot_status,
            'admin_count': len(admin_manager.get_global_admin_list())
        })
        
    except Exception as e:
        logger.error(f"İstatistik API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Global admin yönetimi için API
@app.route('/api/add_global_admin', methods=['POST'])
def api_add_global_admin():
    """API: Global admin ekleme"""
    try:
        data = request.get_json()
        admin_id = data.get('admin_id')
        
        if not admin_id:
            return jsonify({'success': False, 'error': 'Admin ID gerekli'})
        
        from admin_utils import admin_manager
        success = admin_manager.add_global_admin(admin_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Global admin eklendi'})
        else:
            return jsonify({'success': False, 'error': 'Admin eklenemedi'})
            
    except Exception as e:
        logger.error(f"Global admin ekleme hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/remove_global_admin', methods=['POST'])
def api_remove_global_admin():
    """API: Global admin kaldırma"""
    try:
        data = request.get_json()
        admin_id = data.get('admin_id')
        
        if not admin_id:
            return jsonify({'success': False, 'error': 'Admin ID gerekli'})
        
        from admin_utils import admin_manager
        success = admin_manager.remove_global_admin(admin_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Global admin kaldırıldı'})
        else:
            return jsonify({'success': False, 'error': 'Admin kaldırılamadı'})
            
    except Exception as e:
        logger.error(f"Global admin kaldırma hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/list_global_admins')
def api_list_global_admins():
    """API: Global admin listesi"""
    try:
        from admin_utils import admin_manager
        admins = admin_manager.get_global_admin_list()
        
        return jsonify({'success': True, 'admins': admins})
        
    except Exception as e:
        logger.error(f"Global admin listesi hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Bot durumu API
@app.route('/api/bot_status')
def api_bot_status():
    """API: Bot durumu"""
    try:
        # Bot durumunu kontrol et (basit bir ping)
        status = {
            'running': True,
            'last_check': datetime.now().isoformat(),
            'total_products': 0
        }
        
        # Veritabanından ürün sayısını al
        db = get_db()
        guild_stats = db.get_all_guilds_stats()
        status['total_products'] = sum(stat['product_count'] for stat in guild_stats) if guild_stats else 0
        db.close()
        
        return jsonify({'success': True, 'status': status})
        
    except Exception as e:
        logger.error(f"Bot durumu API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Analitik sayfası
@app.route('/analytics')
def analytics():
    """Analitik ve trend sayfası"""
    try:
        db = get_db()
        
        guild_id = request.args.get('guild_id')
        
        # Basit istatistikler
        products = db.get_all_products()
        
        # Guild filtreleme
        if guild_id:
            products = [p for p in products if str(p.get('guild_id', '')) == str(guild_id)]
        
        # Basit analizler
        deals = []
        alerts = []
        guild_stats = None
        guilds = []
        
        if products:
            # En iyi fırsatlar (indirimli ürünler)
            for product in products:
                if product.get('original_price') and product.get('current_price'):
                    discount = ((product['original_price'] - product['current_price']) / product['original_price']) * 100
                    if discount >= 20:  # %20+ indirim
                        deals.append({
                            'name': product['name'],
                            'current_price': product['current_price'],
                            'original_price': product['original_price'],
                            'discount_percentage': discount,
                            'url': product['url'],
                            'last_updated': product.get('last_updated', 'Bilinmiyor')
                        })
            
            # Guild istatistikleri
            if guild_id:
                total_products = len(products)
                avg_price = sum(p.get('current_price', 0) for p in products) / total_products if total_products > 0 else 0
                today_added = len([p for p in products if p.get('added_date', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
                
                guild_stats = {
                    'total_products': total_products,
                    'avg_price': avg_price,
                    'today_added': today_added
                }
        
        # Sunucu listesi
        guild_ids = list(set(str(p.get('guild_id', '')) for p in db.get_all_products() if p.get('guild_id')))
        for gid in guild_ids:
            if gid and gid != 'None':
                guild_products = [p for p in db.get_all_products() if str(p.get('guild_id', '')) == gid]
                guilds.append({
                    'guild_id': gid,
                    'product_count': len(guild_products)
                })
        
        db.close()
        
        return render_template('analytics.html',
                             deals=deals[:10],  # İlk 10 fırsat
                             alerts=alerts[:10],  # İlk 10 uyarı
                             guild_stats=guild_stats,
                             guilds=guilds,
                             selected_guild=guild_id)
    except Exception as e:
        logger.error(f"Analitik sayfası yüklenirken hata: {e}")
        return render_template('analytics.html',
                             deals=[],
                             alerts=[],
                             guild_stats=None,
                             guilds=[],
                             selected_guild=None)

# API: Ürün trend analizi
@app.route('/api/product_trend/<product_id>')
def api_product_trend(product_id):
    """API: Ürün fiyat trendi"""
    try:
        db = get_db()
        from price_analyzer import PriceAnalyzer
        analyzer = PriceAnalyzer(db)
        
        days = int(request.args.get('days', 30))
        trend_data = analyzer.get_price_trend(product_id, days=days)
        
        db.close()
        
        if trend_data and trend_data.get('price_history'):
            return jsonify({'success': True, 'trend': trend_data})
        else:
            return jsonify({'success': False, 'error': 'Yeterli fiyat verisi bulunamadı'})
            
    except Exception as e:
        logger.error(f"Trend API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: En iyi fırsatlar
@app.route('/api/deals')
def api_deals():
    """API: En iyi fırsatlar"""
    try:
        db = get_db()
        from price_analyzer import PriceAnalyzer
        analyzer = PriceAnalyzer(db)
        
        guild_id = request.args.get('guild_id')
        limit = int(request.args.get('limit', 10))
        
        deals = analyzer.get_best_deals(guild_id=guild_id, limit=limit)
        
        db.close()
        
        return jsonify({'success': True, 'deals': deals})
        
    except Exception as e:
        logger.error(f"Fırsatlar API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Fiyat uyarıları
@app.route('/api/alerts')
def api_alerts():
    """API: Fiyat uyarıları"""
    try:
        db = get_db()
        from price_analyzer import PriceAnalyzer
        analyzer = PriceAnalyzer(db)
        
        guild_id = request.args.get('guild_id')
        threshold = int(request.args.get('threshold', 10))
        
        alerts = analyzer.get_price_alerts(guild_id=guild_id, threshold=threshold)
        
        db.close()
        
        return jsonify({'success': True, 'alerts': alerts})
        
    except Exception as e:
        logger.error(f"Uyarılar API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Ürünler listesi
@app.route('/api/products')
def api_products():
    """API: Ürünler listesi"""
    try:
        db = get_db()
        
        guild_id = request.args.get('guild_id')
        products = db.get_all_products(guild_id=guild_id, is_admin=True)
        
        db.close()
        
        return jsonify({'success': True, 'products': products})
        
    except Exception as e:
        logger.error(f"Ürünler API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Bildirimler sayfası
@app.route('/notifications')
def notifications():
    """Bildirimler ve fiyat hedefleri sayfası"""
    return render_template('notifications.html')

# API: Fiyat hedefi ekleme
@app.route('/api/add_price_target', methods=['POST'])
def api_add_price_target():
    """API: Fiyat hedefi ekleme"""
    try:
        data = request.get_json()
        product_url = data.get('product_url')
        target_price = data.get('target_price')
        condition = data.get('condition', 'below')
        
        if not product_url or not target_price:
            return jsonify({'success': False, 'error': 'Ürün URL ve hedef fiyat gerekli'})
        
        # URL'den product_id çıkar
        if not fallback:
            init_components()
        
        product_data = fallback.get_product_info(product_url)
        if not product_data or not product_data.get('success'):
            return jsonify({'success': False, 'error': 'Ürün bilgileri alınamadı'})
        
        product_id = product_data['product_id']
        
        # Bildirim sistemi
        db = get_db()
        from notification_system import NotificationSystem
        notification_system = NotificationSystem(db)
        
        success = notification_system.add_price_target(
            product_id=product_id,
            user_id='web_user',  # Web kullanıcısı için sabit ID
            guild_id='web_guild',
            channel_id='web_channel',
            target_price=target_price,
            condition=condition
        )
        
        db.close()
        
        if success:
            return jsonify({'success': True, 'message': 'Fiyat hedefi eklendi'})
        else:
            return jsonify({'success': False, 'error': 'Fiyat hedefi eklenemedi'})
            
    except Exception as e:
        logger.error(f"Fiyat hedefi ekleme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Fiyat hedefleri listesi
@app.route('/api/price_targets')
def api_price_targets():
    """API: Kullanıcının fiyat hedefleri"""
    try:
        db = get_db()
        from notification_system import NotificationSystem
        notification_system = NotificationSystem(db)
        
        targets = notification_system.get_user_price_targets('web_user', 'web_guild')
        
        db.close()
        
        return jsonify({'success': True, 'targets': targets})
        
    except Exception as e:
        logger.error(f"Fiyat hedefleri API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Fiyat hedefi kaldırma
@app.route('/api/remove_price_target', methods=['POST'])
def api_remove_price_target():
    """API: Fiyat hedefi kaldırma"""
    try:
        data = request.get_json()
        target_id = data.get('target_id')
        
        if not target_id:
            return jsonify({'success': False, 'error': 'Hedef ID gerekli'})
        
        db = get_db()
        from notification_system import NotificationSystem
        notification_system = NotificationSystem(db)
        
        success = notification_system.remove_price_target(target_id, 'web_user')
        
        db.close()
        
        if success:
            return jsonify({'success': True, 'message': 'Fiyat hedefi kaldırıldı'})
        else:
            return jsonify({'success': False, 'error': 'Fiyat hedefi bulunamadı'})
            
    except Exception as e:
        logger.error(f"Fiyat hedefi kaldırma API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Bildirim geçmişi
@app.route('/api/notification_history')
def api_notification_history():
    """API: Bildirim geçmişi"""
    try:
        db = get_db()
        from notification_system import NotificationSystem
        notification_system = NotificationSystem(db)
        
        notifications = notification_system.get_notification_history('web_user', 'web_guild')
        
        db.close()
        
        return jsonify({'success': True, 'notifications': notifications})
        
    except Exception as e:
        logger.error(f"Bildirim geçmişi API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Bildirimleri okundu işaretle
@app.route('/api/mark_notifications_read', methods=['POST'])
def api_mark_notifications_read():
    """API: Bildirimleri okundu işaretle"""
    try:
        db = get_db()
        from notification_system import NotificationSystem
        notification_system = NotificationSystem(db)
        
        count = notification_system.mark_notifications_read('web_user')
        
        db.close()
        
        return jsonify({'success': True, 'marked_count': count})
        
    except Exception as e:
        logger.error(f"Bildirimler işaretleme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Ürün test etme
@app.route('/api/test_product', methods=['POST'])
def api_test_product():
    """API: Ürün URL'sini test etme"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL gerekli'})
        
        if not fallback:
            init_components()
        
        # Ürün bilgilerini test et
        product_data = fallback.get_product_info(url)
        
        if product_data and product_data.get('success'):
            return jsonify({
                'success': True,
                'product': {
                    'name': product_data.get('name'),
                    'price': product_data.get('current_price'),
                    'original_price': product_data.get('original_price'),
                    'image_url': product_data.get('image_url'),
                    'source': product_data.get('source', 'unknown')
                }
            })
        else:
            return jsonify({
                'success': False, 
                'error': product_data.get('error', 'Ürün bilgileri alınamadı')
            })
            
    except Exception as e:
        logger.error(f"Ürün test API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Ayarlar sayfası
@app.route('/settings')
def settings():
    """Ayarlar sayfası"""
    try:
        # Mevcut ayarları oku
        current_settings = {
            'check_interval': os.getenv('CHECK_INTERVAL', '3600'),
            'proxy_enabled': os.getenv('PROXY_ENABLED', 'False'),
            'verify_ssl': os.getenv('VERIFY_SSL', 'True'),
            'timeout': os.getenv('TIMEOUT', '15'),
            'max_retries': os.getenv('MAX_RETRIES', '5'),
            'global_admin_ids': os.getenv('GLOBAL_ADMIN_IDS', ''),
        }
        
        return render_template('settings.html', settings=current_settings)
    except Exception as e:
        logger.error(f"Ayarlar sayfası yüklenirken hata: {e}")
        return render_template('error.html', error=str(e))

# WebSocket bağlantıları
@socketio.on('connect')
def handle_connect():
    """WebSocket bağlantısı"""
    logger.info('Web UI client bağlandı')
    emit('connected', {'status': 'Bağlantı başarılı'})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket bağlantısı kesildi"""
    logger.info('Web UI client bağlantısı kesildi')

# Bot durumu güncelleme thread'i
def update_bot_status():
    """Bot durumunu düzenli olarak günceller"""
    global bot_status
    while True:
        try:
            # Thread-safe database connection
            db = get_db()
            
            # Toplam ürün sayısını güncelle
            guild_stats = db.get_all_guilds_stats()
            bot_status['total_products'] = sum(stat['product_count'] for stat in guild_stats) if guild_stats else 0
            bot_status['last_check'] = datetime.now().isoformat()
            bot_status['running'] = True  # Web UI çalışıyorsa bot da çalışıyor kabul et
            
            db.close()
            
            # WebSocket ile güncelleme gönder
            socketio.emit('status_update', bot_status)
            
            time.sleep(30)  # 30 saniyede bir güncelle
        except Exception as e:
            logger.error(f"Bot durumu güncellenirken hata: {e}")
            bot_status['running'] = False
            time.sleep(60)

def run_web_ui(host='0.0.0.0', port=5000, debug=False):
    """Web UI'yi başlat"""
    try:
        # Bileşenleri başlat
        if not init_components():
            logger.error("Web UI bileşenleri başlatılamadı!")
            return False
        
        # Bot durumu güncelleme thread'ini başlat
        status_thread = threading.Thread(target=update_bot_status, daemon=True)
        status_thread.start()
        
        logger.info(f"Web UI başlatılıyor: http://{host}:{port}")
        
        # Flask uygulamasını başlat
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
        
        return True
        
    except Exception as e:
        logger.error(f"Web UI başlatılırken hata: {e}")
        return False

# Monitoring API Endpoints
@app.route('/api/monitoring/status')
def monitoring_status_api():
    """API: Monitoring durumu"""
    try:
        from site_monitor import site_monitor
        
        # Mevcut yapıyı al
        current_structure = site_monitor.load_previous_structure()
        
        if current_structure:
            last_check = datetime.fromisoformat(current_structure.last_check)
            next_check = last_check + timedelta(hours=48)
            
            status_data = {
                'system_active': True,
                'last_check': current_structure.last_check,
                'next_check': next_check.isoformat(),
                'has_changes': False,  # Bu gerçek bir değişiklik kontrolü gerektirir
                'structure': {
                    'json_ld_present': current_structure.json_ld_present,
                    'price_selectors': current_structure.price_selectors,
                    'title_selectors': current_structure.title_selectors,
                    'image_selectors': current_structure.image_selectors,
                    'api_endpoints': current_structure.api_endpoints,
                    'page_structure_hash': current_structure.page_structure_hash
                },
                'log': [
                    {
                        'timestamp': current_structure.last_check,
                        'message': 'Site yapısı kontrol edildi',
                        'type': 'success'
                    }
                ]
            }
        else:
            status_data = {
                'system_active': False,
                'last_check': None,
                'next_check': None,
                'has_changes': False,
                'structure': None,
                'log': []
            }
        
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"Monitoring status API hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitoring/check', methods=['POST'])
def monitoring_check_api():
    """API: Manuel monitoring kontrolü"""
    try:
        from site_monitor import site_monitor
        import asyncio
        
        # Async fonksiyonu çalıştır (basit bir mock bot ile)
        class MockBot:
            async def fetch_user(self, user_id):
                return None
        
        mock_bot = MockBot()
        
        # Monitoring kontrolünü çalıştır
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(site_monitor.run_monitoring_check(mock_bot))
            return jsonify({'success': True, 'message': 'Monitoring kontrolü tamamlandı'})
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Monitoring check API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/monitoring')
def monitoring_page():
    """Monitoring sayfası"""
    return render_template('monitoring.html')

if __name__ == '__main__':
    # Geliştirme modu
    run_web_ui(debug=True)