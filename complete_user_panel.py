#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Complete User Panel - All in One
Kullanici paneli, tunnel ve tum gereksinimler tek dosyada
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from flask import Flask, render_template_string, jsonify, request, redirect, session
from dotenv import load_dotenv

# .env dosyasini yukle
load_dotenv()

# Flask uygulamasi
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'temp-secret-key-12345')

# Global degiskenler
tunnel_url = None
tunnel_process = None

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trendyol Bot - User Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .container { padding-top: 50px; }
        .card { 
            border-radius: 20px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            background: rgba(255,255,255,0.95);
        }
        .btn-custom {
            border-radius: 25px;
            padding: 12px 30px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
        }
        .tunnel-info {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body p-5">
                        <div class="text-center mb-4">
                            <h1 class="text-success mb-3">✅ Trendyol Bot User Panel</h1>
                            <span class="status-badge bg-success text-white">Active & Running</span>
                        </div>
                        
                        <div class="row text-center mb-4">
                            <div class="col-md-4">
                                <div class="p-3">
                                    <h5>Port</h5>
                                    <span class="badge bg-primary fs-6">{{ port }}</span>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="p-3">
                                    <h5>Status</h5>
                                    <span class="badge bg-success fs-6">Online</span>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="p-3">
                                    <h5>OAuth</h5>
                                    <span class="badge bg-info fs-6">Ready</span>
                                </div>
                            </div>
                        </div>

                        {% if tunnel_url %}
                        <div class="tunnel-info">
                            <h6><i class="fas fa-globe"></i> Tunnel URL:</h6>
                            <a href="{{ tunnel_url }}" target="_blank" class="text-decoration-none">
                                <strong>{{ tunnel_url }}</strong>
                            </a>
                            <br><small class="text-muted">Discord OAuth icin bu URL'yi kullanin</small>
                        </div>
                        {% endif %}

                        <div class="row g-3">
                            <div class="col-md-6">
                                <a href="/test" class="btn btn-primary btn-custom w-100">
                                    <i class="fas fa-vial"></i> API Test
                                </a>
                            </div>
                            <div class="col-md-6">
                                <a href="/auth/callback" class="btn btn-secondary btn-custom w-100">
                                    <i class="fab fa-discord"></i> OAuth Test
                                </a>
                            </div>
                            <div class="col-md-6">
                                <a href="/health" class="btn btn-success btn-custom w-100">
                                    <i class="fas fa-heartbeat"></i> Health Check
                                </a>
                            </div>
                            <div class="col-md-6">
                                <a href="/info" class="btn btn-info btn-custom w-100">
                                    <i class="fas fa-info-circle"></i> System Info
                                </a>
                            </div>
                        </div>

                        <hr class="my-4">
                        
                        <div class="text-center">
                            <h6 class="text-muted">Discord OAuth Setup</h6>
                            <p class="small text-muted">
                                Redirect URI: <code>{{ tunnel_url or 'http://localhost:' + port|string }}/auth/callback</code>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js"></script>
</body>
</html>
'''

# Flask Routes
@app.route('/')
def home():
    port = int(os.getenv('USER_PANEL_PORT', 8080))
    return render_template_string(HTML_TEMPLATE, port=port, tunnel_url=tunnel_url)

@app.route('/test')
def test():
    return jsonify({
        'status': 'OK',
        'message': 'User panel is working perfectly',
        'port': int(os.getenv('USER_PANEL_PORT', 8080)),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'tunnel_url': tunnel_url,
        'oauth_ready': True
    })

@app.route('/auth/callback')
def auth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    return render_template_string('''
    <div class="container mt-5">
        <div class="card">
            <div class="card-body text-center">
                <h2 class="text-success">✅ Discord OAuth Callback</h2>
                <p class="lead">OAuth callback endpoint is working!</p>
                {% if code %}
                    <div class="alert alert-info">
                        <strong>Authorization Code:</strong> {{ code[:20] }}...
                    </div>
                {% endif %}
                <a href="/" class="btn btn-primary">Back to Home</a>
            </div>
        </div>
    </div>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    ''', code=code)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'trendyol-user-panel',
        'port': int(os.getenv('USER_PANEL_PORT', 8080)),
        'uptime': 'active',
        'tunnel_status': 'active' if tunnel_url else 'inactive',
        'tunnel_url': tunnel_url
    })

@app.route('/info')
def info():
    return jsonify({
        'system': {
            'python_version': sys.version,
            'platform': sys.platform,
            'cwd': os.getcwd()
        },
        'config': {
            'port': int(os.getenv('USER_PANEL_PORT', 8080)),
            'flask_secret_key_set': bool(os.getenv('FLASK_SECRET_KEY')),
            'discord_client_id_set': bool(os.getenv('DISCORD_CLIENT_ID')),
            'discord_client_secret_set': bool(os.getenv('DISCORD_CLIENT_SECRET'))
        },
        'tunnel': {
            'url': tunnel_url,
            'active': bool(tunnel_url)
        }
    })

def install_requirements():
    """Gerekli kutuphaneleri yukle"""
    required_packages = ['flask', 'python-dotenv', 'requests']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed")

def start_tunnel():
    """Ngrok tunnel baslat"""
    global tunnel_url, tunnel_process
    
    port = int(os.getenv('USER_PANEL_PORT', 8080))
    
    # Ngrok varsa kullan
    ngrok_path = None
    for path in ['ngrok.exe', 'ngrok', 'C:\\ngrok\\ngrok.exe']:
        if os.path.exists(path) or subprocess.run(['where', path], capture_output=True).returncode == 0:
            ngrok_path = path
            break
    
    if ngrok_path:
        print(f"🌐 Starting ngrok tunnel on port {port}...")
        try:
            tunnel_process = subprocess.Popen([ngrok_path, 'http', str(port)], 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE)
            time.sleep(3)  # Tunnel'in baslamasini bekle
            
            # Ngrok API'den URL al
            try:
                import requests
                response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
                if response.status_code == 200:
                    tunnels = response.json()['tunnels']
                    if tunnels:
                        tunnel_url = tunnels[0]['public_url']
                        print(f"✅ Tunnel active: {tunnel_url}")
                        return tunnel_url
            except:
                pass
        except Exception as e:
            print(f"❌ Ngrok tunnel failed: {e}")
    
    # LocalTunnel dene
    try:
        print(f"🌐 Trying LocalTunnel on port {port}...")
        tunnel_process = subprocess.Popen(['lt', '--port', str(port)], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        text=True)
        
        # LocalTunnel output'unu oku
        for line in tunnel_process.stdout:
            if 'your url is:' in line:
                tunnel_url = line.split('your url is:')[1].strip()
                print(f"✅ LocalTunnel active: {tunnel_url}")
                return tunnel_url
    except Exception as e:
        print(f"❌ LocalTunnel failed: {e}")
    
    print("⚠️  No tunnel service available")
    return None

def main():
    """Ana fonksiyon"""
    print("=" * 60)
    print("🚀 TRENDYOL BOT - COMPLETE USER PANEL")
    print("=" * 60)
    
    # UTF-8 encoding ayarla
    os.environ['PYTHONUTF8'] = '1'
    
    # Gereksinimler
    print("📦 Checking requirements...")
    install_requirements()
    
    # Port ayari
    port = int(os.getenv('USER_PANEL_PORT', 8080))
    host = os.getenv('USER_PANEL_HOST', '0.0.0.0')
    
    print(f"🌐 Starting user panel on {host}:{port}")
    
    # Tunnel'i arka planda baslat
    tunnel_thread = threading.Thread(target=start_tunnel, daemon=True)
    tunnel_thread.start()
    
    # Flask uygulamasini baslat
    print("✅ User panel starting...")
    print(f"📱 Local URL: http://localhost:{port}")
    print("🌐 Tunnel URL will be displayed when ready")
    print("=" * 60)
    
    try:
        # Tarayiciyi ac
        threading.Timer(2, lambda: webbrowser.open(f'http://localhost:{port}')).start()
        
        # Flask baslat
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 User panel stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Tunnel process'ini temizle
        if tunnel_process:
            tunnel_process.terminate()

if __name__ == '__main__':
    main()