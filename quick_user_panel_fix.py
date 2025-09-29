#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Kullanıcı Paneli Hızlı Çözüm
Port 3000'de basit Flask sunucusu başlatır
"""

import os
import sys
from flask import Flask, render_template_string

# Basit Flask uygulaması
app = Flask(__name__)
app.secret_key = 'temporary-secret-key-for-testing'

# Basit ana sayfa
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kullanıcı Paneli Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            .container { max-width: 600px; margin: 0 auto; text-align: center; }
            .success { color: green; }
            .info { color: blue; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="success">✅ Kullanıcı Paneli Çalışıyor!</h1>
            <p class="info">Port 3000 başarıyla dinleniyor</p>
            <p>Cloudflare Tunnel: <strong>https://sale-trustee-bike-academy.trycloudflare.com</strong></p>
            <hr>
            <h3>Test Linkleri:</h3>
            <p><a href="/test">Test Sayfası</a></p>
            <p><a href="/auth/callback">OAuth Callback Test</a></p>
        </div>
    </body>
    </html>
    ''')

@app.route('/test')
def test():
    return {'status': 'OK', 'message': 'Kullanıcı paneli çalışıyor', 'port': 3000}

@app.route('/auth/callback')
def auth_callback():
    return render_template_string('''
    <h1>OAuth Callback Test</h1>
    <p>Bu sayfa Discord OAuth callback için hazır</p>
    <p><a href="/">Ana Sayfaya Dön</a></p>
    ''')

if __name__ == '__main__':
    print("=" * 50)
    print("Kullanıcı Paneli Hızlı Test Başlatılıyor")
    print("=" * 50)
    print("Port: 3000")
    print("URL: http://localhost:3000")
    print("Cloudflare: https://sale-trustee-bike-academy.trycloudflare.com")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=3000, debug=True)
    except Exception as e:
        print(f"Hata: {e}")
        print("Port 3000 kullanımda olabilir!")
        
        # Alternatif port dene
        print("Port 3001 deneniyor...")
        try:
            app.run(host='0.0.0.0', port=3001, debug=True)
        except Exception as e2:
            print(f"Port 3001 de başarısız: {e2}")