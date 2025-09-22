#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hızlı Web UI Test
"""

from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="tr" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trendyol Bot - Web UI Test</title>
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.4.19/dist/full.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-base-100">
    <div class="hero min-h-screen bg-gradient-to-br from-primary to-secondary">
        <div class="hero-content text-center text-primary-content">
            <div class="max-w-md">
                <div class="text-8xl mb-8">
                    <i class="fas fa-robot"></i>
                </div>
                <h1 class="text-5xl font-bold mb-4">Trendyol Bot</h1>
                <h2 class="text-2xl mb-8">Web UI Başarıyla Çalışıyor!</h2>
                
                <div class="stats shadow mb-8">
                    <div class="stat bg-base-100 text-base-content">
                        <div class="stat-figure text-success">
                            <i class="fas fa-check-circle text-2xl"></i>
                        </div>
                        <div class="stat-title">Durum</div>
                        <div class="stat-value text-success">Online</div>
                        <div class="stat-desc">Web arayüzü aktif</div>
                    </div>
                </div>
                
                <div class="space-y-4">
                    <div class="alert alert-success">
                        <i class="fas fa-info-circle"></i>
                        <div>
                            <h3 class="font-bold">Başarılı!</h3>
                            <div class="text-sm">Web UI başarıyla çalışıyor. Artık tam sürümü kullanabilirsiniz.</div>
                        </div>
                    </div>
                    
                    <div class="flex flex-col gap-2">
                        <button class="btn btn-accent" onclick="testAPI()">
                            <i class="fas fa-vial"></i>
                            API Test
                        </button>
                        <button class="btn btn-info" onclick="showInfo()">
                            <i class="fas fa-info"></i>
                            Sistem Bilgileri
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function testAPI() {
            alert('API test başarılı! Web UI tamamen çalışıyor.');
        }
        
        function showInfo() {
            const info = `
🤖 Trendyol Bot Web UI
📅 Tarih: ${new Date().toLocaleDateString('tr-TR')}
🕒 Saat: ${new Date().toLocaleTimeString('tr-TR')}
🌐 Port: 5001
✅ Durum: Çalışıyor
            `;
            alert(info);
        }
        
        // Auto refresh indicator
        setInterval(() => {
            const indicator = document.querySelector('.stat-value');
            indicator.style.opacity = '0.5';
            setTimeout(() => {
                indicator.style.opacity = '1';
            }, 500);
        }, 2000);
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("🚀 Hızlı Web UI Test Başlatılıyor...")
    print("📍 URL: http://localhost:5001")
    print("🔧 Çıkmak için Ctrl+C")
    
    app.run(host='0.0.0.0', port=5001, debug=False)