import requests
import json
import os
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import hmac
import base64

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrendyolAPI:
    """
    Trendyol Marketplace API entegrasyonu
    Resmi API kullanarak ürün bilgilerini çeker
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, supplier_id: str = None):
        """
        Trendyol API client'ını başlatır
        
        Args:
            api_key: Trendyol API anahtarı
            api_secret: Trendyol API gizli anahtarı  
            supplier_id: Tedarikçi ID'si
        """
        self.api_key = api_key or os.getenv('TRENDYOL_API_KEY')
        self.api_secret = api_secret or os.getenv('TRENDYOL_API_SECRET')
        self.supplier_id = supplier_id or os.getenv('TRENDYOL_SUPPLIER_ID')
        
        self.base_url = "https://api.trendyol.com"
        self.timeout = 30
        
        # API credentials kontrolü
        if not all([self.api_key, self.api_secret, self.supplier_id]):
            logger.warning("Trendyol API credentials eksik. Sadece public endpoint'ler kullanılabilir.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TrendyolBot/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _generate_signature(self, method: str, url: str, timestamp: str) -> str:
        """API imzası oluşturur"""
        try:
            # Signature string oluştur
            signature_string = f"{method.upper()}\n{url}\n{timestamp}"
            
            # HMAC-SHA256 ile imzala
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                signature_string.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            # Base64 encode
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            logger.error(f"Signature oluşturma hatası: {e}")
            return ""
    
    def _make_authenticated_request(self, method: str, endpoint: str, data: dict = None) -> Optional[dict]:
        """Kimlik doğrulamalı API isteği yapar"""
        try:
            url = f"{self.base_url}{endpoint}"
            timestamp = str(int(time.time() * 1000))
            
            # Signature oluştur
            signature = self._generate_signature(method, endpoint, timestamp)
            
            # Headers
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{self.api_key}:{self.api_secret}".encode()).decode()}',
                'X-Trendyol-Timestamp': timestamp,
                'X-Trendyol-Signature': signature
            }
            
            self.session.headers.update(headers)
            
            # İstek yap
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Desteklenmeyen HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API isteği hatası: {e}")
            return None
        except Exception as e:
            logger.error(f"Genel API hatası: {e}")
            return None
    
    def _make_public_request(self, endpoint: str) -> Optional[dict]:
        """Public API isteği yapar (kimlik doğrulama gerektirmez)"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Public API isteği hatası: {e}")
            return None
    
    def get_product_by_id(self, product_id: str) -> Optional[dict]:
        """
        Ürün ID'si ile ürün bilgilerini getirir
        
        Args:
            product_id: Trendyol ürün ID'si
            
        Returns:
            Ürün bilgileri dict'i veya None
        """
        try:
            logger.info(f"API ile ürün bilgileri çekiliyor: {product_id}")
            
            # Önce supplier products endpoint'ini dene (authenticated)
            if self.api_key and self.api_secret and self.supplier_id:
                endpoint = f"/sapigw/suppliers/{self.supplier_id}/products/{product_id}"
                result = self._make_authenticated_request('GET', endpoint)
                
                if result:
                    return self._parse_supplier_product(result, product_id)
            
            # Public search endpoint'ini dene
            search_result = self.search_products(product_id)
            if search_result and search_result.get('products'):
                for product in search_result['products']:
                    if str(product.get('id')) == str(product_id):
                        return self._parse_search_product(product)
            
            # Alternatif public endpoint'ler
            public_endpoints = [
                f"/api/v1/product/{product_id}",
                f"/api/product/{product_id}",
                f"/public/product/{product_id}"
            ]
            
            for endpoint in public_endpoints:
                result = self._make_public_request(endpoint)
                if result:
                    return self._parse_public_product(result, product_id)
            
            logger.warning(f"Ürün bulunamadı: {product_id}")
            return None
            
        except Exception as e:
            logger.error(f"Ürün getirme hatası: {e}")
            return None
    
    def search_products(self, query: str, limit: int = 10) -> Optional[dict]:
        """
        Ürün arama yapar
        
        Args:
            query: Arama sorgusu (ürün adı, ID, vs.)
            limit: Maksimum sonuç sayısı
            
        Returns:
            Arama sonuçları dict'i veya None
        """
        try:
            # Public search endpoint
            endpoint = f"/api/v1/search"
            params = {
                'q': query,
                'limit': limit,
                'offset': 0
            }
            
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            
            logger.warning(f"Arama başarısız: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Arama hatası: {e}")
            return None
    
    def get_product_prices(self, product_id: str) -> Optional[dict]:
        """
        Ürün fiyat bilgilerini getirir
        
        Args:
            product_id: Ürün ID'si
            
        Returns:
            Fiyat bilgileri dict'i veya None
        """
        try:
            if not all([self.api_key, self.api_secret, self.supplier_id]):
                logger.warning("Fiyat bilgileri için API credentials gerekli")
                return None
            
            endpoint = f"/sapigw/suppliers/{self.supplier_id}/products/{product_id}/price-and-inventory"
            result = self._make_authenticated_request('GET', endpoint)
            
            if result:
                return {
                    'product_id': product_id,
                    'sale_price': result.get('salePrice'),
                    'list_price': result.get('listPrice'),
                    'quantity': result.get('quantity'),
                    'currency': 'TRY'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Fiyat getirme hatası: {e}")
            return None
    
    def _parse_supplier_product(self, data: dict, product_id: str) -> dict:
        """Supplier API yanıtını parse eder"""
        try:
            return {
                'product_id': product_id,
                'name': data.get('title', ''),
                'url': f"https://www.trendyol.com/sr?q=&pi={product_id}",
                'image_url': data.get('images', [{}])[0].get('url') if data.get('images') else None,
                'current_price': float(data.get('salePrice', 0)),
                'original_price': float(data.get('listPrice', data.get('salePrice', 0))),
                'stock': data.get('quantity', 0),
                'brand': data.get('brand', ''),
                'category': data.get('categoryName', ''),
                'success': True,
                'source': 'supplier_api'
            }
        except Exception as e:
            logger.error(f"Supplier product parse hatası: {e}")
            return {'success': False, 'error': 'Parse hatası'}
    
    def _parse_search_product(self, data: dict) -> dict:
        """Search API yanıtını parse eder"""
        try:
            product_id = str(data.get('id', ''))
            return {
                'product_id': product_id,
                'name': data.get('name', ''),
                'url': f"https://www.trendyol.com{data.get('url', '')}" if data.get('url') else f"https://www.trendyol.com/sr?q=&pi={product_id}",
                'image_url': data.get('image', {}).get('url') if data.get('image') else None,
                'current_price': float(data.get('price', {}).get('discountedPrice', 0)),
                'original_price': float(data.get('price', {}).get('originalPrice', data.get('price', {}).get('discountedPrice', 0))),
                'rating': data.get('rating', 0),
                'review_count': data.get('ratingCount', 0),
                'success': True,
                'source': 'search_api'
            }
        except Exception as e:
            logger.error(f"Search product parse hatası: {e}")
            return {'success': False, 'error': 'Parse hatası'}
    
    def _parse_public_product(self, data: dict, product_id: str) -> dict:
        """Public API yanıtını parse eder"""
        try:
            return {
                'product_id': product_id,
                'name': data.get('name', data.get('title', '')),
                'url': f"https://www.trendyol.com/sr?q=&pi={product_id}",
                'image_url': data.get('imageUrl', data.get('image')),
                'current_price': float(data.get('currentPrice', data.get('price', 0))),
                'original_price': float(data.get('originalPrice', data.get('currentPrice', data.get('price', 0)))),
                'success': True,
                'source': 'public_api'
            }
        except Exception as e:
            logger.error(f"Public product parse hatası: {e}")
            return {'success': False, 'error': 'Parse hatası'}
    
    def extract_product_id_from_url(self, url: str) -> Optional[str]:
        """URL'den ürün ID'sini çıkarır"""
        try:
            if url.isdigit():
                return url
            
            # Kısaltılmış link ise önce tam URL'yi al
            if 'ty.gl' in url or 'tyml.gl' in url:
                logger.info(f"Kısaltılmış API linkten ID çıkarılıyor: {url}")
                try:
                    import requests
                    response = requests.head(url, allow_redirects=True, timeout=10)
                    url = response.url
                    logger.info(f"API tam URL alındı: {url}")
                except Exception as e:
                    logger.warning(f"Kısaltılmış link çözülemedi: {e}")
            
            import re
            patterns = [
                r'/[^/]+-p-(\d+)',      # Standard format
                r'productId[=:](\d+)',   # Query parameter
                r'pi[=:](\d+)',          # Short parameter
                r'/p/(\d+)',             # Short format
                r'p-(\d+)',              # Anywhere in URL
                r'\d{8,}'                # 8+ digit numbers
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    if len(match.groups()) > 0:
                        return match.group(1)
                    else:
                        return match.group(0)
            
            return None
        except Exception as e:
            logger.error(f"URL'den ID çıkarma hatası: {e}")
            return None
    
    def is_valid_url(self, url: str) -> bool:
        """URL'nin geçerli olup olmadığını kontrol eder"""
        if url.isdigit():
            return True
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            # Trendyol domainleri ve kısaltılmış linkler
            valid_domains = ["trendyol.com", "ty.gl", "tyml.gl", "trendyol-milla.com"]
            return any(domain in parsed.netloc.lower() for domain in valid_domains)
        except:
            return False
    
    def get_product_info(self, url_or_id: str) -> dict:
        """
        Ana ürün bilgisi getirme fonksiyonu
        URL veya ID ile ürün bilgilerini çeker
        
        Args:
            url_or_id: Ürün URL'si veya ID'si
            
        Returns:
            Ürün bilgileri dict'i
        """
        try:
            # URL'den ID çıkar
            product_id = self.extract_product_id_from_url(url_or_id)
            if not product_id:
                return {'success': False, 'error': 'Geçersiz ürün ID veya URL'}
            
            # URL doğrulama
            if not self.is_valid_url(url_or_id):
                return {'success': False, 'error': 'Geçersiz Trendyol URL'}
            
            logger.info(f"Ürün bilgileri API ile çekiliyor: {product_id}")
            
            # API ile ürün bilgilerini çek
            product_data = self.get_product_by_id(product_id)
            
            if product_data and product_data.get('success'):
                logger.info(f"Ürün başarıyla çekildi: {product_data.get('name', 'İsimsiz')}")
                return product_data
            else:
                return {'success': False, 'error': 'Ürün bilgileri API\'den alınamadı'}
                
        except Exception as e:
            logger.error(f"Ürün bilgisi getirme hatası: {e}")
            return {'success': False, 'error': f'Hata: {str(e)}'}


class TrendyolAPIFallback:
    """
    Trendyol API için fallback sınıfı
    API çalışmadığında scraping'e geri döner
    """
    
    def __init__(self, api_client: TrendyolAPI = None, scraper = None):
        self.api_client = api_client
        self.scraper = scraper
        
    def get_product_info(self, url_or_id: str) -> dict:
        """
        Önce API'yi dener, başarısız olursa scraping'e geçer
        """
        try:
            # Önce API'yi dene
            if self.api_client:
                logger.info("API ile deneniyor...")
                result = self.api_client.get_product_info(url_or_id)
                if result and result.get('success'):
                    return result
                logger.warning("API başarısız, scraping'e geçiliyor...")
            
            # API başarısız olursa scraping'e geç
            if self.scraper:
                logger.info("Scraping ile deneniyor...")
                result = self.scraper.scrape_product(url_or_id)
                if result and result.get('success'):
                    result['source'] = 'scraping'
                    return result
            
            return {'success': False, 'error': 'Hem API hem scraping başarısız'}
            
        except Exception as e:
            logger.error(f"Fallback hatası: {e}")
            return {'success': False, 'error': f'Fallback hatası: {str(e)}'}