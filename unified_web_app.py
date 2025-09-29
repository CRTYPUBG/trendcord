#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unified Web Application - Admin & User Panel
Tek Cloudflare tunnel üzerinden hem admin hem user girişi
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
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
from user_auth import UserManager, DiscordOAuth, login_required, admin_required, guild_access_required
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Flask uygulaması
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'trendyol-unified-secret-key-2024')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global değişkenler
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
        logger.info("Unified Web App bileşenleri başarıyla başlatıldı")
        return True
    except Exception as e:
        logger.error(f"Unified Web App bileşenleri başlatılırken hata: {e}")
        return False

def get_db():
    """Thread-safe database connection"""
    return Database()

# ==================== ANA SAYFALAR ====================

@app.route('/')
def index():
    """Ana giriş sayfası - Kullanıcı tipini seç"""
    return render_template('unified_login.html')

@app.route('/login')
def login():
    """Giriş sayfası"""
    login_type = request.args.get('type', 'user')
    
    if login_type == 'admin':
        return render_template('admin_login.html')
    else:
        # Discord OAuth için URL oluştur
        db = get_db()
        user_manager = UserManager(db)
        oauth_url = user_manager.oauth.get_authorization_url()
        db.close()
        
        if oauth_url:
            return redirect(oauth_url)
        else:
            flash('Discord OAuth yapılandırması eksik!', 'error')
            return render_template('error.html', error='Discord OAuth yapılandırması eksik')

# ==================== ADMIN GİRİŞİ ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin giriş işlemi"""
    if request.method == 'POST':
        admin_key = request.form.get('admin_key')
        
        # Admin anahtarını kontrol et
        if admin_key == os.getenv('ADMIN_SECRET_KEY', 'admin123'):
            session['is_admin'] = True
            session['admin_logged_in'] = True
            session['login_time'] = datetime.now().isoformat()
            
            flash('Admin girişi başarılı!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Geçersiz admin anahtarı!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        db = get_db()
        
        # İstatistikler
        stats = {
            'total_products': 0,
            'total_guilds': 0,
            'total_users': 0,
            'recent_products': [],
            'guild_stats': []
        }
        
        try:
            # Genel istatistikler
            all_stats = db.get_all_guilds_stats()
            stats['total_guilds'] = len(all_stats) if all_stats else 0
            stats['total_products'] = sum(stat['product_count'] for stat in all_stats) if all_stats else 0
            stats['guild_stats'] = all_stats[:10] if all_stats else []
            
            # Kullanıcı sayısı
            user_count = db.cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1').fetchone()
            stats['total_users'] = user_count[0] if user_count else 0
            
            # Son eklenen ürünler
            recent_products = db.get_all_products(is_admin=True)
            stats['recent_products'] = recent_products[:10] if recent_products else []
        except Exception as e:
            logger.error(f"Admin istatistik hesaplama hatası: {e}")
        
        db.close()
        
        return render_template('admin_dashboard.html', 
                             stats=stats, 
                             bot_status=bot_status)
    except Exception as e:
        logger.error(f"Admin dashboard yüklenirken hata: {e}")
        return render_template('error.html', error=str(e))

# ==================== USER GİRİŞİ (DISCORD OAUTH) ====================

@app.route('/auth/callback')
def auth_callback():
    """Discord OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            flash(f'Discord OAuth hatası: {error}', 'error')
            return redirect(url_for('index'))
        
        if not code:
            flash('Yetkilendirme kodu alınamadı!', 'error')
            return redirect(url_for('index'))
        
        db = get_db()
        user_manager = UserManager(db)
        
        # OAuth kodunu token ile değiştir
        token_data = user_manager.oauth.exchange_code(code, state)
        if not token_data:
            db.close()
            flash('Token değişimi başarısız!', 'error')
            return redirect(url_for('index'))
        
        # Kullanıcı bilgilerini al
        user_info = user_manager.oauth.get_user_info(token_data['access_token'])
        if not user_info:
            db.close()
            flash('Kullanıcı bilgileri alınamadı!', 'error')
            return redirect(url_for('index'))
        
        # Kullanıcıyı oluştur/güncelle
        user_id = user_manager.create_or_update_user(
            user_info['user'], 
            user_info['guilds']
        )
        
        if not user_id:
            db.close()
            flash('Kullanıcı kaydı başarısız!', 'error')
            return redirect(url_for('index'))
        
        # Oturum oluştur
        session_token = user_manager.create_session(
            user_id,
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        db.close()
        
        if session_token:
            session['session_token'] = session_token
            session['is_user'] = True
            session['user_logged_in'] = True
            
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Oturum oluşturulamadı!', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"OAuth callback hatası: {e}")
        flash('Giriş işlemi sırasında hata oluştu!', 'error')
        return redirect(url_for('index'))

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """Kullanıcı dashboard"""
    try:
        db = get_db()
        user_manager = UserManager(db)
        
        # Kullanıcının sunucularını al
        user_guilds = user_manager.get_user_guilds(request.current_user['user_id'])
        
        # Kullanıcının ürünlerini al
        user_products = []
        for guild in user_guilds:
            guild_products = db.get_all_products(guild_id=guild['guild_id'])
            user_products.extend(guild_products)
        
        # İstatistikler
        stats = {
            'total_products': len(user_products),
            'total_guilds': len(user_guilds),
            'recent_products': user_products[:5]
        }
        
        db.close()
        
        return render_template('user_dashboard.html',
                             user=request.current_user,
                             guilds=user_guilds,
                             stats=stats,
                             products=user_products[:10])
    except Exception as e:
        logger.error(f"User dashboard yüklenirken hata: {e}")
        return render_template('error.html', error=str(e))

# ==================== ORTAK SAYFALAR ====================

@app.route('/products')
def products():
    """Ürünler sayfası - Admin ve User için ortak"""
    try:
        db = get_db()
        
        # Kullanıcı tipini kontrol et
        is_admin = session.get('is_admin', False)
        is_user = session.get('is_user', False)
        
        if not is_admin and not is_user:
            return redirect(url_for('index'))
        
        guild_id = request.args.get('guild_id')
        page = int(request.args.get('page', 1))
        per_page = 20
        
        # Admin ise tüm ürünleri, user ise sadece erişimi olan sunucuların ürünlerini göster
        if is_admin:
            all_products = db.get_all_products(guild_id=guild_id, is_admin=True)
            guild_stats = db.get_all_guilds_stats()
        else:
            # User için sadece erişimi olan sunucuların ürünleri
            user_manager = UserManager(db)
            user_guilds = user_manager.get_user_guilds(request.current_user['user_id'])
            
            if guild_id and not any(g['guild_id'] == guild_id for g in user_guilds):
                db.close()
                flash('Bu sunucuya erişim yetkiniz yok!', 'error')
                return redirect(url_for('user_dashboard'))
            
            all_products = []
            for guild in user_guilds:
                if not guild_id or guild['guild_id'] == guild_id:
                    guild_products = db.get_all_products(guild_id=guild['guild_id'])
                    all_products.extend(guild_products)
            
            guild_stats = [{'guild_id': g['guild_id'], 'guild_name': g['guild_name']} for g in user_guilds]
        
        # Sayfalama
        start = (page - 1) * per_page
        end = start + per_page
        products = all_products[start:end]
        
        # Sayfa bilgileri
        total_pages = (len(all_products) + per_page - 1) // per_page
        
        db.close()
        
        template = 'admin_products.html' if is_admin else 'user_products.html'
        
        return render_template(template,
                             products=products,
                             guild_stats=guild_stats,
                             current_guild=guild_id,
                             page=page,
                             total_pages=total_pages,
                             total_products=len(all_products))
    except Exception as e:
        logger.error(f"Ürünler sayfası yüklenirken hata: {e}")
        return render_template('error.html', error=str(e))

# ==================== API ENDPOINTS ====================

@app.route('/api/add_product', methods=['POST'])
def api_add_product():
    """API: Yeni ürün ekleme"""
    try:
        # Yetki kontrolü
        is_admin = session.get('is_admin', False)
        is_user = session.get('is_user', False)
        
        if not is_admin and not is_user:
            return jsonify({'success': False, 'error': 'Giriş gerekli'})
        
        data = request.get_json()
        url = data.get('url')
        guild_id = data.get('guild_id', 'web_ui')
        user_id = data.get('user_id', 'web_admin')
        channel_id = data.get('channel_id', 'web_channel')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL gerekli'})
        
        # User ise sunucu erişimi kontrol et
        if is_user and not is_admin:
            db = get_db()
            user_manager = UserManager(db)
            
            if not user_manager.has_guild_access(request.current_user['user_id'], guild_id):
                db.close()
                return jsonify({'success': False, 'error': 'Bu sunucuya erişim yetkiniz yok'})
            
            db.close()
        
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

@app.route('/api/delete_product', methods=['POST'])
def api_delete_product():
    """API: Ürün silme"""
    try:
        # Yetki kontrolü
        is_admin = session.get('is_admin', False)
        is_user = session.get('is_user', False)
        
        if not is_admin and not is_user:
            return jsonify({'success': False, 'error': 'Giriş gerekli'})
        
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({'success': False, 'error': 'Ürün ID gerekli'})
        
        # User ise ürünün sahibi mi kontrol et (basit kontrol)
        if is_user and not is_admin:
            # Bu kısım daha detaylı yetki kontrolü gerektirebilir
            pass
        
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

@app.route('/api/stats')
def api_stats():
    """API: İstatistikler"""
    try:
        # Yetki kontrolü
        is_admin = session.get('is_admin', False)
        is_user = session.get('is_user', False)
        
        if not is_admin and not is_user:
            return jsonify({'success': False, 'error': 'Giriş gerekli'})
        
        db = get_db()
        
        if is_admin:
            # Admin için tüm istatistikler
            guild_stats = db.get_all_guilds_stats()
            total_products = sum(stat['product_count'] for stat in guild_stats)
            user_count = db.cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1').fetchone()
            
            stats = {
                'total_guilds': len(guild_stats),
                'total_products': total_products,
                'total_users': user_count[0] if user_count else 0,
                'guild_stats': guild_stats,
                'bot_status': bot_status
            }
        else:
            # User için sadece erişimi olan sunucuların istatistikleri
            user_manager = UserManager(db)
            user_guilds = user_manager.get_user_guilds(request.current_user['user_id'])
            
            total_products = 0
            for guild in user_guilds:
                guild_products = db.get_all_products(guild_id=guild['guild_id'])
                total_products += len(guild_products)
            
            stats = {
                'total_guilds': len(user_guilds),
                'total_products': total_products,
                'guild_stats': user_guilds
            }
        
        db.close()
        
        return jsonify({'success': True, **stats})
        
    except Exception as e:
        logger.error(f"İstatistik API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ==================== ÇIKIŞ ====================

@app.route('/logout')
def logout():
    """Çıkış işlemi"""
    try:
        # User oturumunu sonlandır
        if session.get('session_token'):
            db = get_db()
            user_manager = UserManager(db)
            user_manager.logout_user(session.get('session_token'))
            db.close()
        
        # Session'ı temizle
        session.clear()
        flash('Başarıyla çıkış yaptınız!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Çıkış işlemi hatası: {e}")
        session.clear()
        return redirect(url_for('index'))

# ==================== WEBSOCKET ====================

@socketio.on('connect')
def handle_connect():
    """WebSocket bağlantısı"""
    logger.info('Unified Web App client bağlandı')
    emit('connected', {'status': 'Bağlantı başarılı'})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket bağlantısı kesildi"""
    logger.info('Unified Web App client bağlantısı kesildi')

# ==================== BOT DURUMU ====================

def update_bot_status():
    """Bot durumunu düzenli olarak günceller"""
    global bot_status
    while True:
        try:
            db = get_db()
            
            # Toplam ürün sayısını güncelle
            guild_stats = db.get_all_guilds_stats()
            bot_status['total_products'] = sum(stat['product_count'] for stat in guild_stats) if guild_stats else 0
            bot_status['last_check'] = datetime.now().isoformat()
            bot_status['running'] = True
            
            db.close()
            
            # WebSocket ile güncelleme gönder
            socketio.emit('status_update', bot_status)
            
            time.sleep(30)  # 30 saniyede bir güncelle
        except Exception as e:
            logger.error(f"Bot durumu güncellenirken hata: {e}")
            bot_status['running'] = False
            time.sleep(60)

def run_unified_app(host='0.0.0.0', port=5000, debug=False):
    """Unified Web App'i başlat"""
    try:
        # Bileşenleri başlat
        if not init_components():
            logger.error("Unified Web App bileşenleri başlatılamadı!")
            return False
        
        # Bot durumu güncelleme thread'ini başlat
        status_thread = threading.Thread(target=update_bot_status, daemon=True)
        status_thread.start()
        
        logger.info(f"Unified Web App başlatılıyor: http://{host}:{port}")
        logger.info("Admin giriş: /login?type=admin")
        logger.info("User giriş: /login?type=user")
        
        # Flask uygulamasını başlat
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
        
        return True
        
    except Exception as e:
        logger.error(f"Unified Web App başlatılırken hata: {e}")
        return False

if __name__ == '__main__':
    # Port ve host ayarları
    port = int(os.getenv('WEB_PORT', 5000))
    host = os.getenv('WEB_HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    run_unified_app(host=host, port=port, debug=debug)