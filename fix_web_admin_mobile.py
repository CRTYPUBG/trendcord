#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Admin Mobil Düzeltme Scripti
Otomatik olarak web admin panelindeki mobil görünüm sorunlarını düzeltir
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Dosyayı yedekle"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"✅ Yedek oluşturuldu: {backup_path}")
        return backup_path
    return None

def fix_base_template():
    """Base template'i mobil uyumlu hale getir"""
    template_path = "templates/base.html"
    
    if not os.path.exists(template_path):
        print(f"❌ {template_path} bulunamadı")
        return False
    
    backup_file(template_path)
    
    # Mobil uyumlu base template
    mobile_base_content = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{% block title %}TrendCord Admin{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #7c3aed;
            --secondary-color: #a855f7;
            --dark-bg: #1a1a2e;
            --card-bg: #16213e;
            --text-light: #e2e8f0;
        }
        
        body {
            background: linear-gradient(135deg, var(--dark-bg) 0%, #0f172a 100%);
            color: var(--text-light);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        
        /* Mobil responsive navbar */
        .navbar {
            background: rgba(26, 26, 46, 0.95) !important;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(124, 58, 237, 0.3);
            padding: 0.5rem 1rem;
        }
        
        .navbar-brand {
            font-weight: bold;
            color: var(--primary-color) !important;
            font-size: 1.2rem;
        }
        
        /* Mobil menü düzeltmeleri */
        .navbar-toggler {
            border: none;
            padding: 0.25rem 0.5rem;
        }
        
        .navbar-toggler:focus {
            box-shadow: none;
        }
        
        .navbar-nav .nav-link {
            color: var(--text-light) !important;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            margin: 0.2rem 0;
            transition: all 0.3s ease;
        }
        
        .navbar-nav .nav-link:hover {
            background: rgba(124, 58, 237, 0.2);
            color: white !important;
        }
        
        /* Kart tasarımları */
        .card {
            background: var(--card-bg);
            border: 1px solid rgba(124, 58, 237, 0.3);
            border-radius: 1rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin-bottom: 1.5rem;
        }
        
        .card-header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            border-bottom: none;
            border-radius: 1rem 1rem 0 0 !important;
            padding: 1rem 1.5rem;
        }
        
        .card-title {
            color: white;
            margin: 0;
            font-weight: 600;
        }
        
        /* Mobil tablo düzeltmeleri */
        .table-responsive {
            border-radius: 0.5rem;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        .table {
            color: var(--text-light);
            margin: 0;
            min-width: 600px; /* Minimum genişlik */
        }
        
        .table th {
            background: rgba(124, 58, 237, 0.2);
            border-color: rgba(124, 58, 237, 0.3);
            font-weight: 600;
            white-space: nowrap;
            padding: 0.75rem 0.5rem;
            font-size: 0.9rem;
        }
        
        .table td {
            border-color: rgba(124, 58, 237, 0.2);
            padding: 0.75rem 0.5rem;
            vertical-align: middle;
            font-size: 0.85rem;
        }
        
        /* Buton düzeltmeleri */
        .btn {
            border-radius: 0.5rem;
            font-weight: 500;
            padding: 0.5rem 1rem;
            margin: 0.2rem;
            white-space: nowrap;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            border: none;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #dc2626, #ef4444);
            border: none;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #059669, #10b981);
            border: none;
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #d97706, #f59e0b);
            border: none;
        }
        
        /* Form düzeltmeleri */
        .form-control, .form-select {
            background: rgba(22, 33, 62, 0.8);
            border: 1px solid rgba(124, 58, 237, 0.3);
            color: var(--text-light);
            border-radius: 0.5rem;
        }
        
        .form-control:focus, .form-select:focus {
            background: rgba(22, 33, 62, 0.9);
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(124, 58, 237, 0.25);
            color: var(--text-light);
        }
        
        /* Mobil responsive düzeltmeler */
        @media (max-width: 768px) {
            .container-fluid {
                padding: 0.5rem;
            }
            
            .card {
                margin-bottom: 1rem;
            }
            
            .card-body {
                padding: 1rem;
            }
            
            .btn {
                font-size: 0.8rem;
                padding: 0.4rem 0.8rem;
                margin: 0.1rem;
            }
            
            .table th, .table td {
                padding: 0.5rem 0.3rem;
                font-size: 0.8rem;
            }
            
            .navbar-brand {
                font-size: 1rem;
            }
            
            h1, h2, h3 {
                font-size: 1.2rem;
            }
            
            /* Mobil için özel sınıflar */
            .mobile-stack {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .mobile-hide {
                display: none;
            }
        }
        
        @media (max-width: 576px) {
            .container-fluid {
                padding: 0.25rem;
            }
            
            .card-body {
                padding: 0.75rem;
            }
            
            .btn {
                font-size: 0.75rem;
                padding: 0.3rem 0.6rem;
            }
            
            .table {
                font-size: 0.75rem;
                min-width: 500px;
            }
        }
        
        /* Loading animasyonu */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Alert düzeltmeleri */
        .alert {
            border-radius: 0.5rem;
            border: none;
            margin-bottom: 1rem;
        }
        
        .alert-success {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border-left: 4px solid #10b981;
        }
        
        .alert-danger {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border-left: 4px solid #ef4444;
        }
        
        .alert-warning {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border-left: 4px solid #f59e0b;
        }
        
        .alert-info {
            background: rgba(124, 58, 237, 0.2);
            color: var(--primary-color);
            border-left: 4px solid var(--primary-color);
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-chart-line me-2"></i>TrendCord Admin
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">
                            <i class="fas fa-home me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/products">
                            <i class="fas fa-box me-1"></i>Products
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/notifications">
                            <i class="fas fa-bell me-1"></i>Notifications
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-3">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Mobil dokunmatik iyileştirmeleri
        document.addEventListener('DOMContentLoaded', function() {
            // Touch feedback için
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(btn => {
                btn.addEventListener('touchstart', function() {
                    this.style.transform = 'scale(0.95)';
                });
                btn.addEventListener('touchend', function() {
                    this.style.transform = 'scale(1)';
                });
            });
            
            // Tablo kaydırma ipucu
            const tables = document.querySelectorAll('.table-responsive');
            tables.forEach(table => {
                if (table.scrollWidth > table.clientWidth) {
                    table.setAttribute('title', 'Kaydırarak daha fazla görebilirsiniz');
                }
            });
        });
        
        // Loading state için yardımcı fonksiyon
        function showLoading(element) {
            const originalText = element.innerHTML;
            element.innerHTML = '<span class="loading"></span> Loading...';
            element.disabled = true;
            return originalText;
        }
        
        function hideLoading(element, originalText) {
            element.innerHTML = originalText;
            element.disabled = false;
        }
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>'''
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(mobile_base_content)
    
    print(f"✅ {template_path} mobil uyumlu hale getirildi")
    return True

def main():
    """Ana düzeltme fonksiyonu"""
    print("🚀 Web Admin Mobil Düzeltme Scripti Başlatılıyor...")
    print("=" * 50)
    
    # Templates klasörünü kontrol et
    if not os.path.exists("templates"):
        os.makedirs("templates")
        print("✅ Templates klasörü oluşturuldu")
    
    success_count = 0
    total_fixes = 1
    
    # Base template düzelt
    if fix_base_template():
        success_count += 1
    
    print("=" * 50)
    print(f"✅ Düzeltme tamamlandı: {success_count}/{total_fixes} başarılı")
    
    if success_count == total_fixes:
        print("🎉 Mobil düzeltmeler başarıyla uygulandı!")
        print("\n📱 Mobil iyileştirmeler:")
        print("- Responsive tasarım")
        print("- Touch-friendly butonlar")
        print("- Mobil menü")
        print("- Kaydırılabilir tablolar")
        print("- Optimized form layouts")
    else:
        print("⚠️  Bazı düzeltmeler başarısız oldu. Lütfen hataları kontrol edin.")
    
    print("\n🔄 Web sunucusunu yeniden başlatmayı unutmayın!")

if __name__ == "__main__":
    main()