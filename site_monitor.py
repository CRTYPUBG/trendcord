"""
Trendyol Site Monitoring System
Trendyol'un HTML yapısını ve API'sini izler, değişiklikleri tespit eder
"""

import asyncio
import json
import logging
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from bs4 import BeautifulSoup
import os
from dataclasses import dataclass, asdict
from config import GLOBAL_ADMIN_IDS

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SiteStructure:
    """Site yapısını temsil eden sınıf"""
    json_ld_present: bool
    price_selectors: List[str]
    title_selectors: List[str]
    image_selectors: List[str]
    api_endpoints: List[str]
    page_structure_hash: str
    last_check: str
    
class SiteMonitor:
    """Trendyol site yapısını izleyen sınıf"""
    
    def __init__(self):
        self.monitor_file = "site_structure.json"
        self.test_urls = [
            "https://ty.gl/reii1wcijhbf1",  # Gerçek test edilmiş mobil link
            "https://www.trendyol.com/apple/iphone-15-128-gb-p-773358088",
            "https://www.trendyol.com/pun-wear/unisex-oversize-kalip-cay-cicegibeyaz-t-shirt-100-pamuk-p-956534756"
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def load_previous_structure(self) -> Optional[SiteStructure]:
        """Önceki site yapısını yükle"""
        try:
            if os.path.exists(self.monitor_file):
                with open(self.monitor_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return SiteStructure(**data)
        except Exception as e:
            logger.error(f"Önceki yapı yüklenirken hata: {e}")
        return None
    
    def save_structure(self, structure: SiteStructure):
        """Site yapısını kaydet"""
        try:
            with open(self.monitor_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(structure), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Yapı kaydedilirken hata: {e}")
    
    def analyze_page_structure(self, url: str) -> Dict:
        """Sayfa yapısını analiz et"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # JSON-LD kontrolü
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            json_ld_present = len(json_ld_scripts) > 0
            
            # Fiyat selektörleri
            price_selectors = []
            price_patterns = [
                r'price["\']?\s*:\s*["\']?(\d+[.,]\d+)',
                r'currentPrice["\']?\s*:\s*["\']?(\d+[.,]\d+)',
                r'sellingPrice["\']?\s*:\s*["\']?(\d+[.,]\d+)'
            ]
            
            for pattern in price_patterns:
                if re.search(pattern, response.text):
                    price_selectors.append(pattern)
            
            # Başlık selektörleri
            title_selectors = []
            title_elements = [
                'h1.pr-new-br span',
                'h1 span',
                '.product-name',
                '[data-testid="product-name"]'
            ]
            
            for selector in title_elements:
                if soup.select(selector):
                    title_selectors.append(selector)
            
            # Resim selektörleri
            image_selectors = []
            image_elements = [
                '.product-image img',
                '[data-testid="product-image"] img',
                '.gallery img'
            ]
            
            for selector in image_elements:
                if soup.select(selector):
                    image_selectors.append(selector)
            
            # Sayfa yapısı hash'i
            important_elements = soup.find_all(['script', 'div', 'span'], 
                                             attrs={'class': re.compile(r'(price|product|gallery)')})
            structure_text = ''.join([str(elem) for elem in important_elements[:50]])  # İlk 50 element
            page_hash = hashlib.md5(structure_text.encode()).hexdigest()
            
            return {
                'json_ld_present': json_ld_present,
                'price_selectors': price_selectors,
                'title_selectors': title_selectors,
                'image_selectors': image_selectors,
                'page_structure_hash': page_hash,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Sayfa analizi hatası ({url}): {e}")
            return {'success': False, 'error': str(e)}
    
    def check_api_endpoints(self) -> List[str]:
        """API endpoint'lerini kontrol et"""
        api_endpoints = []
        
        # Bilinen API endpoint'leri test et
        test_endpoints = [
            "https://public-mdc.trendyol.com/discovery-web-productdetailgw-service/api/productDetail/",
            "https://public-mdc.trendyol.com/discovery-web-searchgw-service/api/search",
            "https://api.trendyol.com/webapi/products/"
        ]
        
        for endpoint in test_endpoints:
            try:
                # Test product ID ile kontrol
                test_url = f"{endpoint}123456" if endpoint.endswith('/') else f"{endpoint}?q=test"
                response = requests.head(test_url, headers=self.headers, timeout=10)
                
                # 404 değil ise endpoint aktif
                if response.status_code != 404:
                    api_endpoints.append(endpoint)
                    
            except Exception as e:
                logger.debug(f"API endpoint test hatası ({endpoint}): {e}")
        
        return api_endpoints
    
    def analyze_current_structure(self) -> SiteStructure:
        """Mevcut site yapısını analiz et"""
        logger.info("Site yapısı analizi başlıyor...")
        
        all_price_selectors = set()
        all_title_selectors = set()
        all_image_selectors = set()
        json_ld_count = 0
        all_hashes = []
        
        # Test URL'lerini analiz et
        for url in self.test_urls:
            logger.info(f"Analiz ediliyor: {url}")
            result = self.analyze_page_structure(url)
            
            if result.get('success'):
                if result.get('json_ld_present'):
                    json_ld_count += 1
                
                all_price_selectors.update(result.get('price_selectors', []))
                all_title_selectors.update(result.get('title_selectors', []))
                all_image_selectors.update(result.get('image_selectors', []))
                all_hashes.append(result.get('page_structure_hash', ''))
            
            # Rate limiting
            import time
            time.sleep(2)
        
        # API endpoint'lerini kontrol et
        api_endpoints = self.check_api_endpoints()
        
        # Genel yapı hash'i
        combined_hash = hashlib.md5(''.join(sorted(all_hashes)).encode()).hexdigest()
        
        return SiteStructure(
            json_ld_present=json_ld_count > 0,
            price_selectors=list(all_price_selectors),
            title_selectors=list(all_title_selectors),
            image_selectors=list(all_image_selectors),
            api_endpoints=api_endpoints,
            page_structure_hash=combined_hash,
            last_check=datetime.now().isoformat()
        )
    
    def compare_structures(self, old: SiteStructure, new: SiteStructure) -> Dict:
        """İki yapıyı karşılaştır ve değişiklikleri tespit et"""
        changes = {
            'has_changes': False,
            'critical_changes': [],
            'minor_changes': [],
            'improvements': []
        }
        
        # JSON-LD değişikliği
        if old.json_ld_present != new.json_ld_present:
            change_type = 'critical' if not new.json_ld_present else 'improvement'
            message = f"JSON-LD desteği {'kaldırıldı' if not new.json_ld_present else 'eklendi'}"
            changes[f'{change_type}_changes'].append(message)
            changes['has_changes'] = True
        
        # Fiyat selektörleri
        old_price = set(old.price_selectors)
        new_price = set(new.price_selectors)
        
        if old_price != new_price:
            removed_price = old_price - new_price
            added_price = new_price - old_price
            
            if removed_price:
                changes['critical_changes'].append(f"Fiyat selektörleri kaldırıldı: {list(removed_price)}")
                changes['has_changes'] = True
            
            if added_price:
                changes['improvements'].append(f"Yeni fiyat selektörleri: {list(added_price)}")
                changes['has_changes'] = True
        
        # Başlık selektörleri
        old_title = set(old.title_selectors)
        new_title = set(new.title_selectors)
        
        if old_title != new_title:
            removed_title = old_title - new_title
            added_title = new_title - old_title
            
            if removed_title:
                changes['minor_changes'].append(f"Başlık selektörleri değişti: -{list(removed_title)}")
                changes['has_changes'] = True
            
            if added_title:
                changes['minor_changes'].append(f"Yeni başlık selektörleri: +{list(added_title)}")
                changes['has_changes'] = True
        
        # API endpoint'leri
        old_api = set(old.api_endpoints)
        new_api = set(new.api_endpoints)
        
        if old_api != new_api:
            removed_api = old_api - new_api
            added_api = new_api - old_api
            
            if removed_api:
                changes['critical_changes'].append(f"API endpoint'leri kaldırıldı: {list(removed_api)}")
                changes['has_changes'] = True
            
            if added_api:
                changes['improvements'].append(f"Yeni API endpoint'leri: {list(added_api)}")
                changes['has_changes'] = True
        
        # Sayfa yapısı hash'i
        if old.page_structure_hash != new.page_structure_hash:
            changes['minor_changes'].append("Sayfa yapısında değişiklik tespit edildi")
            changes['has_changes'] = True
        
        return changes
    
    def generate_update_suggestions(self, changes: Dict) -> List[str]:
        """Değişikliklere göre güncelleme önerileri oluştur"""
        suggestions = []
        
        if changes.get('critical_changes'):
            suggestions.append("🚨 KRİTİK: Scraper kodunu güncellemeniz gerekiyor!")
            suggestions.append("📝 Önerilen aksiyonlar:")
            suggestions.append("  - scraper.py dosyasını kontrol edin")
            suggestions.append("  - Yeni selektörleri test edin")
            suggestions.append("  - Fallback mekanizmalarını aktifleştirin")
        
        if changes.get('minor_changes'):
            suggestions.append("⚠️ UYARI: Küçük değişiklikler tespit edildi")
            suggestions.append("📝 Önerilen aksiyonlar:")
            suggestions.append("  - Test scriptlerini çalıştırın")
            suggestions.append("  - Log dosyalarını kontrol edin")
        
        if changes.get('improvements'):
            suggestions.append("✅ İYİLEŞTİRME: Yeni özellikler tespit edildi")
            suggestions.append("📝 Önerilen aksiyonlar:")
            suggestions.append("  - Yeni özellikleri entegre etmeyi düşünün")
            suggestions.append("  - Performans iyileştirmeleri yapabilirsiniz")
        
        return suggestions
    
    async def send_dm_to_admins(self, bot, message: str):
        """Global adminlere DM gönder"""
        try:
            for admin_id in GLOBAL_ADMIN_IDS:
                try:
                    user = await bot.fetch_user(int(admin_id))
                    await user.send(message)
                    logger.info(f"DM gönderildi: {admin_id}")
                except Exception as e:
                    logger.error(f"DM gönderilemedi ({admin_id}): {e}")
        except Exception as e:
            logger.error(f"Admin DM hatası: {e}")
    
    async def run_monitoring_check(self, bot):
        """Ana monitoring kontrolü"""
        try:
            logger.info("🔍 Site monitoring kontrolü başlıyor...")
            
            # Mevcut yapıyı analiz et
            current_structure = self.analyze_current_structure()
            
            # Önceki yapıyı yükle
            previous_structure = self.load_previous_structure()
            
            if previous_structure is None:
                # İlk çalıştırma
                self.save_structure(current_structure)
                message = (
                    "🤖 **Trendyol Site Monitoring Başlatıldı**\n\n"
                    "✅ İlk analiz tamamlandı\n"
                    f"📊 JSON-LD Desteği: {'Var' if current_structure.json_ld_present else 'Yok'}\n"
                    f"🔍 Fiyat Selektörleri: {len(current_structure.price_selectors)} adet\n"
                    f"📝 Başlık Selektörleri: {len(current_structure.title_selectors)} adet\n"
                    f"🌐 API Endpoint'leri: {len(current_structure.api_endpoints)} adet\n\n"
                    "🔄 Bundan sonra 2 günde bir kontrol edilecek."
                )
                await self.send_dm_to_admins(bot, message)
                return
            
            # Yapıları karşılaştır
            changes = self.compare_structures(previous_structure, current_structure)
            
            if changes['has_changes']:
                # Değişiklik tespit edildi
                logger.warning("⚠️ Site yapısında değişiklik tespit edildi!")
                
                # Güncelleme önerileri
                suggestions = self.generate_update_suggestions(changes)
                
                # DM mesajı oluştur
                message_parts = [
                    "🚨 **Trendyol Site Değişikliği Tespit Edildi!**\n",
                    f"📅 Kontrol Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                ]
                
                if changes['critical_changes']:
                    message_parts.append("🔴 **Kritik Değişiklikler:**")
                    for change in changes['critical_changes']:
                        message_parts.append(f"  • {change}")
                    message_parts.append("")
                
                if changes['minor_changes']:
                    message_parts.append("🟡 **Küçük Değişiklikler:**")
                    for change in changes['minor_changes']:
                        message_parts.append(f"  • {change}")
                    message_parts.append("")
                
                if changes['improvements']:
                    message_parts.append("🟢 **İyileştirmeler:**")
                    for change in changes['improvements']:
                        message_parts.append(f"  • {change}")
                    message_parts.append("")
                
                if suggestions:
                    message_parts.append("💡 **Öneriler:**")
                    for suggestion in suggestions:
                        message_parts.append(suggestion)
                
                message = "\n".join(message_parts)
                await self.send_dm_to_admins(bot, message)
                
                # Yeni yapıyı kaydet
                self.save_structure(current_structure)
                
            else:
                # Değişiklik yok
                logger.info("✅ Site yapısında değişiklik yok")
                
                # Haftalık özet (7 günde bir)
                last_check = datetime.fromisoformat(previous_structure.last_check)
                if datetime.now() - last_check > timedelta(days=7):
                    message = (
                        "📊 **Haftalık Trendyol Monitoring Raporu**\n\n"
                        "✅ Site yapısında değişiklik tespit edilmedi\n"
                        f"🔍 Son kontrol: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                        f"📈 Sistem durumu: Stabil\n"
                        f"🤖 Bot durumu: Çalışıyor\n\n"
                        "🔄 Bir sonraki kontrol: 2 gün sonra"
                    )
                    await self.send_dm_to_admins(bot, message)
                
                # Yapıyı güncelle (son kontrol tarihi için)
                current_structure.last_check = datetime.now().isoformat()
                self.save_structure(current_structure)
        
        except Exception as e:
            logger.error(f"Monitoring kontrolü hatası: {e}")
            
            # Hata durumunda da adminlere bildir
            error_message = (
                "❌ **Trendyol Site Monitoring Hatası**\n\n"
                f"🚨 Hata: {str(e)}\n"
                f"📅 Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                "🔧 Lütfen sistem loglarını kontrol edin."
            )
            await self.send_dm_to_admins(bot, error_message)

# Global monitor instance
site_monitor = SiteMonitor()