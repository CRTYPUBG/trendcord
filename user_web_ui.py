#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kullanıcı Bazlı Web Arayüzü
Discord OAuth ile güvenli giriş ve kullanıcı paneli
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import logging
from datetime import datetime
from user_auth import UserManager, DiscordOAuth, login_required, admin_required, guild_access_required
from user_database import UserDatabase
from database import Database
from scraper import TrendyolScraper
from trendyol_api import TrendyolAPI, TrendyolAPIFallback
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
scraper = None
api_client = None
fallback = None

def init_components():
    """Bot bileşenlerini başlat"""
    global scraper, api_client, fallback
    try:
        scraper = TrendyolScraper(use_proxy=False, verify_ssl=True)
        api_client = TrendyolAPI()
        fallback = TrendyolAPIFallback(api_client=api_client, scraper=scraper)
        logger.info("Kullanıcı Web UI bileşenleri başarıyla başlatıldı")
        return True
    except Exception as e:
        logger.error(f"Kullanıcı Web UI bileşenleri başlatılırken hata: {e}")
        return False

# Ana sayfa - Giriş kontrolü ile
@app.route('/')
def index():
    """Ana sayfa - giriş yapmış kullanıcılar için dashboard"""
    session_token = session.get('session_token')
    if not session_token:
        return redirect(url_for('login'))
    
    # Oturum doğrula
    db = Database()
    user_manager = UserManager(db)
    user_data = user_manager.validate_session(session_token)
    db.close()
    
    if not user_data:
        session.clear()
        return redirect(url_for('login'))
    
    return redirect(url_for('dashboard'))

# Giriş sayfası
@app.route('/login')
def login():
    """Discord OAuth giriş sayfası"""
    # Zaten giriş yapmışsa dashboard'a yönlendir
    session_token = session.get('session_token')
    if session_token:
        db = Database()
        user_manager = UserManager(db)
        user_data = user_manager.validate_session(session_token)
        db.close()
        
        if user_data:
            return redirect(url_for('dashboard'))
    
    # Discord OAuth URL'sini oluştur
    oauth = DiscordOAuth()
    auth_url = oauth.get_authorization_url()
    
    if not auth_url:
        flash('Discord OAuth yapılandırması eksik. Lütfen yöneticiye başvurun.', 'error')
        return render_template('login.html', auth_url=None)
    
    return render_template('login.html', auth_url=auth_url)

# Discord OAuth callback
@app.route('/auth/callback')
def auth_callback():
    """Discord OAuth callback işlemi"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            flash(f'Discord giriş hatası: {error}', 'error')
            return redirect(url_for('login'))
        
        if not code:
            flash('Yetkilendirme kodu alınamadı', 'error')
            return redirect(url_for('login'))
        
        # OAuth işlemi
        oauth = DiscordOAuth()
        token_data = oauth.exchange_code(code, state)
        
        if not token_data:
            flash('Discord token alınamadı', 'error')
            return redirect(url_for('login'))
        
        # Kullanıcı bilgilerini al
        user_info = oauth.get_user_info(token_data['access_token'])
        
        if not user_info:
            flash('Kullanıcı bilgileri alınamadı', 'error')
            return redirect(url_for('login'))
        
        # Kullanıcıyı oluştur/güncelle
        db = Database()
        user_manager = UserManager(db)
        
        user_id = user_manager.create_or_update_user(
            user_info['user'], 
            user_info['guilds']
        )
        

        
        if not user_id:
            db.close()
            flash('Kullanıcı oluşturulamadı', 'error')
            return redirect(url_for('login'))
        
        # Oturum oluştur
        session_token = user_manager.create_session(
            user_id,
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        db.close()
        
        if session_token:
            session['session_token'] = session_token
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Oturum oluşturulamadı', 'error')
            return redirect(url_for('login'))
            
    except Exception as e:
        logger.error(f"OAuth callback hatası: {e}")
        flash('Giriş işlemi sırasında hata oluştu', 'error')
        return redirect(url_for('login'))

# Çıkış
@app.route('/logout')
def logout():
    """Kullanıcı çıkışı"""
    session_token = session.get('session_token')
    
    if session_token:
        db = Database()
        user_manager = UserManager(db)
        user_manager.logout_user(session_token)
        db.close()
    
    session.clear()
    flash('Başarıyla çıkış yaptınız', 'info')
    return redirect(url_for('login'))

# Kullanıcı dashboard'u
@app.route('/dashboard')
@login_required
def dashboard():
    """Kullanıcı ana paneli"""
    try:
        user_data = request.current_user
        
        # Kullanıcı veritabanı bağlantısı
        user_db = UserDatabase()
        
        # Kullanıcı istatistikleri
        stats = user_db.get_user_stats(user_data['user_id'])
        
        # Son ürünler
        recent_products = user_db.get_user_products(
            user_data['user_id'], 
            user_data['encryption_key_hash']
        )[:5]  # Son 5 ürün
        
        # Okunmamış bildirimler
        unread_notifications = user_db.get_user_notifications(
            user_data['user_id'],
            user_data['encryption_key_hash'],
            unread_only=True,
            limit=5
        )
        
        # Kullanıcının sunucuları
        db = Database()
        user_manager = UserManager(db)
        user_guilds = user_manager.get_user_guilds(user_data['user_id'])
        db.close()
        
        user_db.close()
        
        return render_template('user_dashboard.html',
                             user=user_data,
                             stats=stats,
                             recent_products=recent_products,
                             unread_notifications=unread_notifications,
                             user_guilds=user_guilds)
                             
    except Exception as e:
        logger.error(f"Dashboard yüklenirken hata: {e}")
        flash('Dashboard yüklenirken hata oluştu', 'error')
        return redirect(url_for('login'))

# Kullanıcı ürünleri
@app.route('/my-products')
@login_required
def my_products():
    """Kullanıcının ürünleri"""
    try:
        user_data = request.current_user
        guild_id = request.args.get('guild_id')
        
        # Sunucu erişim kontrolü
        if guild_id:
            db = Database()
            user_manager = UserManager(db)
            
            if not user_manager.is_global_admin(user_data['discord_id']):
                if not user_manager.has_guild_access(user_data['user_id'], guild_id):
                    db.close()
                    flash('Bu sunucuya erişim yetkiniz yok', 'error')
                    return redirect(url_for('my_products'))
            
            user_guilds = user_manager.get_user_guilds(user_data['user_id'])
            db.close()
        else:
            db = Database()
            user_manager = UserManager(db)
            user_guilds = user_manager.get_user_guilds(user_data['user_id'])
            db.close()
        
        # Kullanıcı ürünleri
        user_db = UserDatabase()
        products = user_db.get_user_products(
            user_data['user_id'],
            user_data['encryption_key_hash'],
            guild_id
        )
        user_db.close()
        
        return render_template('user_products.html',
                             user=user_data,
                             products=products,
                             user_guilds=user_guilds,
                             selected_guild=guild_id)
                             
    except Exception as e:
        logger.error(f"Kullanıcı ürünleri yüklenirken hata: {e}")
        flash('Ürünler yüklenirken hata oluştu', 'error')
        return redirect(url_for('dashboard'))

# Kullanıcı bildirimleri
@app.route('/my-notifications')
@login_required
def my_notifications():
    """Kullanıcının bildirimleri"""
    try:
        user_data = request.current_user
        
        user_db = UserDatabase()
        
        # Tüm bildirimler
        notifications = user_db.get_user_notifications(
            user_data['user_id'],
            user_data['encryption_key_hash'],
            limit=50
        )
        
        # Fiyat hedefleri
        price_targets = user_db.get_user_price_targets(
            user_data['user_id'],
            user_data['encryption_key_hash']
        )
        
        user_db.close()
        
        return render_template('user_notifications.html',
                             user=user_data,
                             notifications=notifications,
                             price_targets=price_targets)
                             
    except Exception as e:
        logger.error(f"Kullanıcı bildirimleri yüklenirken hata: {e}")
        flash('Bildirimler yüklenirken hata oluştu', 'error')
        return redirect(url_for('dashboard'))

# Kullanıcı ayarları
@app.route('/my-settings')
@login_required
def my_settings():
    """Kullanıcı ayarları"""
    try:
        user_data = request.current_user
        
        user_db = UserDatabase()
        settings = user_db.get_user_settings(
            user_data['user_id'],
            user_data['encryption_key_hash']
        )
        user_db.close()
        
        return render_template('user_settings.html',
                             user=user_data,
                             settings=settings)
                             
    except Exception as e:
        logger.error(f"Kullanıcı ayarları yüklenirken hata: {e}")
        flash('Ayarlar yüklenirken hata oluştu', 'error')
        return redirect(url_for('dashboard'))

# API: Kullanıcı ürün ekleme
@app.route('/api/user/add-product', methods=['POST'])
@login_required
def api_user_add_product():
    """API: Kullanıcı ürün ekleme"""
    try:
        user_data = request.current_user
        data = request.get_json()
        
        url = data.get('url')
        guild_id = data.get('guild_id')
        channel_id = data.get('channel_id', 'web')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL gerekli'})
        
        # Sunucu erişim kontrolü
        if guild_id:
            db = Database()
            user_manager = UserManager(db)
            
            if not user_manager.is_global_admin(user_data['discord_id']):
                if not user_manager.has_guild_access(user_data['user_id'], guild_id):
                    db.close()
                    return jsonify({'success': False, 'error': 'Bu sunucuya erişim yetkiniz yok'})
            
            db.close()
        
        # Ürün bilgilerini al
        if not fallback:
            init_components()
        
        product_data = fallback.get_product_info(url)
        
        if not product_data or not product_data.get('success'):
            return jsonify({'success': False, 'error': 'Ürün bilgileri alınamadı'})
        
        # Kullanıcı veritabanına ekle
        user_db = UserDatabase()
        success = user_db.add_user_product(
            user_data['user_id'],
            user_data['encryption_key_hash'],
            product_data,
            guild_id,
            channel_id
        )
        user_db.close()
        
        if success:
            return jsonify({'success': True, 'product': {
                'name': product_data.get('name'),
                'price': product_data.get('current_price'),
                'product_id': product_data.get('product_id')
            }})
        else:
            return jsonify({'success': False, 'error': 'Ürün eklenemedi'})
            
    except Exception as e:
        logger.error(f"Kullanıcı ürün ekleme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Kullanıcı ürün silme
@app.route('/api/user/delete-product', methods=['POST'])
@login_required
def api_user_delete_product():
    """API: Kullanıcı ürün silme"""
    try:
        user_data = request.current_user
        data = request.get_json()
        
        product_id = data.get('product_id')
        guild_id = data.get('guild_id')
        
        if not product_id:
            return jsonify({'success': False, 'error': 'Ürün ID gerekli'})
        
        user_db = UserDatabase()
        success = user_db.delete_user_product(
            user_data['user_id'],
            product_id,
            guild_id
        )
        user_db.close()
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Ürün silinemedi'})
            
    except Exception as e:
        logger.error(f"Kullanıcı ürün silme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Kullanıcı ayarları güncelleme
@app.route('/api/user/update-settings', methods=['POST'])
@login_required
def api_user_update_settings():
    """API: Kullanıcı ayarları güncelleme"""
    try:
        user_data = request.current_user
        settings_data = request.get_json()
        
        user_db = UserDatabase()
        success = user_db.update_user_settings(
            user_data['user_id'],
            user_data['encryption_key_hash'],
            settings_data
        )
        user_db.close()
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Ayarlar güncellenemedi'})
            
    except Exception as e:
        logger.error(f"Kullanıcı ayarları güncelleme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Fiyat hedefi ekleme
@app.route('/api/user/add-price-target', methods=['POST'])
@login_required
def api_user_add_price_target():
    """API: Kullanıcı fiyat hedefi ekleme"""
    try:
        user_data = request.current_user
        data = request.get_json()
        
        product_id = data.get('product_id')
        target_price = data.get('target_price')
        condition = data.get('condition', 'below')
        
        if not product_id or not target_price:
            return jsonify({'success': False, 'error': 'Ürün ID ve hedef fiyat gerekli'})
        
        target_data = {
            'product_id': product_id,
            'target_price': float(target_price),
            'condition': condition,
            'created_at': datetime.now().isoformat()
        }
        
        user_db = UserDatabase()
        success = user_db.add_user_price_target(
            user_data['user_id'],
            user_data['encryption_key_hash'],
            target_data
        )
        user_db.close()
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Fiyat hedefi eklenemedi'})
            
    except Exception as e:
        logger.error(f"Fiyat hedefi ekleme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Bildirimleri okundu işaretle
@app.route('/api/user/mark-notifications-read', methods=['POST'])
@login_required
def api_user_mark_notifications_read():
    """API: Kullanıcı bildirimlerini okundu işaretle"""
    try:
        user_data = request.current_user
        data = request.get_json()
        
        notification_ids = data.get('notification_ids')  # Opsiyonel
        
        user_db = UserDatabase()
        marked_count = user_db.mark_user_notifications_read(
            user_data['user_id'],
            notification_ids
        )
        user_db.close()
        
        return jsonify({'success': True, 'marked_count': marked_count})
        
    except Exception as e:
        logger.error(f"Bildirim işaretleme API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API: Kullanıcı istatistikleri
@app.route('/api/user/stats')
@login_required
def api_user_stats():
    """API: Kullanıcı istatistikleri"""
    try:
        user_data = request.current_user
        
        user_db = UserDatabase()
        stats = user_db.get_user_stats(user_data['user_id'])
        user_db.close()
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        logger.error(f"Kullanıcı istatistikleri API hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Admin paneli (sadece global adminler)
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    """Admin paneli"""
    try:
        # Genel sistem istatistikleri
        db = Database()
        
        # Toplam kullanıcı sayısı
        total_users = db.cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1').fetchone()[0]
        
        # Toplam ürün sayısı (tüm kullanıcılar)
        user_db = UserDatabase()
        total_products = user_db.cursor.execute('SELECT COUNT(*) FROM user_products').fetchone()[0]
        
        # Aktif oturumlar
        active_sessions = db.cursor.execute('''
        SELECT COUNT(*) FROM user_sessions 
        WHERE expires_at > ?
        ''', (datetime.now().isoformat(),)).fetchone()[0]
        
        db.close()
        user_db.close()
        
        admin_stats = {
            'total_users': total_users,
            'total_products': total_products,
            'active_sessions': active_sessions
        }
        
        return render_template('admin_panel.html',
                             user=request.current_user,
                             admin_stats=admin_stats)
                             
    except Exception as e:
        logger.error(f"Admin paneli yüklenirken hata: {e}")
        flash('Admin paneli yüklenirken hata oluştu', 'error')
        return redirect(url_for('dashboard'))

# WebSocket bağlantıları
@socketio.on('connect')
def handle_connect():
    """WebSocket bağlantısı"""
    logger.info('Kullanıcı WebSocket bağlandı')
    emit('connected', {'status': 'Bağlantı başarılı'})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket bağlantısı kesildi"""
    logger.info('Kullanıcı WebSocket bağlantısı kesildi')

def run_user_web_ui(host='0.0.0.0', port=5001, debug=False):
    """Kullanıcı Web UI'yi başlat"""
    try:
        # Bileşenleri başlat
        if not init_components():
            logger.error("Kullanıcı Web UI bileşenleri başlatılamadı!")
            return False
        
        logger.info(f"Kullanıcı Web UI başlatılıyor: http://{host}:{port}")
        
        # Flask uygulamasını başlat
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
        
        return True
        
    except Exception as e:
        logger.error(f"Kullanıcı Web UI başlatılırken hata: {e}")
        return False

if __name__ == '__main__':
    run_user_web_ui(debug=True)