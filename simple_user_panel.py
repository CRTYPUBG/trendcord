#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basit Kullanıcı Paneli
Port 3001'de çalışan minimal Flask uygulaması
"""

import os
import sys
from flask import Flask, render_template_string, jsonify
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Flask uygulaması
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'temporary-secret-key')

# Ana sayfa
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trendyol Bot - User Panel</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { padding-top: 100px; }
            .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center p-5">
                            <h1 class="text-success mb-4">✅ User Panel Active!</h1>
                            <p class="lead">Trendyol Bot User Panel is running successfully</p>
                            <hr>
                            <div class="row text-start">
                                <div class="col-6">
                                    <strong>Port:</strong> {{ port }}
                                </div>
                                <div class="col-6">
                                    <strong>Status:</strong> <span class="text-success">Running</span>
                                </div>
                            </div>
                            <hr>
                            <h5>Test Links:</h5>
                            <div class="d-grid gap-2">
                                <a href="/test" class="btn btn-primary">API Test</a>
                                <a href="/auth/callback" class="btn btn-secondary">OAuth Callback Test</a>
                                <a href="/health" class="btn btn-success">Health Check</a>
                            </div>
                            <hr>
                            <small class="text-muted">
                                Cloudflare Tunnel: Active<br>
                                Discord OAuth: Ready
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', port=os.getenv('USER_PANEL_PORT', '3001'))

@app.route('/test')
def test():
    return jsonify({
        'status': 'OK',
        'message': 'User panel is working',
        'port': int(os.getenv('USER_PANEL_PORT', '3001')),
        'timestamp': '2025-09-23 19:15:00'
    })

@app.route('/auth/callback')
def auth_callback():
    return render_template_string('''
    <div class="container mt-5">
        <div class="alert alert-info">
            <h4>Discord OAuth Callback Test</h4>
            <p>This endpoint is ready for Discord OAuth integration</p>
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
    </div>
    ''')

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'user-panel',
        'port': int(os.getenv('USER_PANEL_PORT', '3001')),
        'uptime': 'active'
    })

def run_simple_user_panel():
    """Basit kullanıcı panelini başlat"""
    host = os.getenv('USER_PANEL_HOST', '0.0.0.0')
    port = int(os.getenv('USER_PANEL_PORT', '3001'))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("=" * 50)
    print("Simple User Panel Starting")
    print("=" * 50)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"URL: http://localhost:{port}")
    print("=" * 50)
    
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"Error starting user panel: {e}")
        return False
    
    return True

if __name__ == '__main__':
    run_simple_user_panel()