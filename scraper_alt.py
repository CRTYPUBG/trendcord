import requests
import random
import re
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import logging
import time
import ssl
import urllib3

# SSL uyarılarını devre dışı bırak
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrendyolScraperAlt:
    def __init__(self, use_proxy=True, timeout=10, max_retries=3, verify_ssl=False):
        """
        Alternatif Trendyol ürün bilgilerini kazıyıcı sınıf.
        API endpoint'lerini ve daha stabil yöntemleri kullanır.
        """
        self.use_proxy = use_proxy
        self.proxies = []
        self.working_proxies = []
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        
        # Daha güncel ve gerçekçi headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not A(Brand";v="8", "Chromium";v="121", "Google Chrome";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Referer': 'https://www.trendyol.com/',
            'Origin': 'https://www.trendyol.com',
            'Connection': 'keep-alive'
        }
        
        if use_proxy:
            self.load_proxies()
    
    def load_proxies(self):
        """Proxy'leri proxies.txt dosyasından yükler."""
        try:
            if os.path.exists("proxies.txt"):
                with open("proxies.txt", "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self.proxies.append(line)
                logger.info(f"{len(self.proxies)} proxy yüklendi.")
            else:
                logger.warning("proxies.txt dosyası bulunamadı!")
        except Exception as e:
            logger.error(f"Proxy yüklenirken hata oluştu: {e}")
    
    def get_random_proxy(self):
        """Rastgele bir proxy döndürür."""
        if not self.proxies and not self.working_proxies:
            return None
        
        if self.working_proxies:
            proxy = random.choice(self.working_proxies)
        else:
            proxy = random.choice(self.proxies)
            
        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    
    def extract_product_id(self, url):
        """URL'den ürün ID'sini çıkarır."""
        try:
            if url.isdigit():
                return url
                
            # Trendyol URL pattern'leri
            patterns = [
                r'/[^/]+-p-(\d+)',  # Standard format: /product-name-p-123456
                r'productId[=:](\d+)',  # Query parameter
                r'pi[=:](\d+)',  # Short parameter
                r'/p/(\d+)',  # Short format
                r'p-(\d+)',  # Anywhere in URL
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
                    
            return None
        except Exception as e:
            logger.error(f"Ürün ID çıkarılırken hata: {e}")
            return None
    
    def scrape_product(self, url):
        """
        Ürün bilgilerini çeker. Önce API endpoint'lerini dener, 
        başarısız olursa HTML scraping yapar.
        """
        product_id = self.extract_product_id(url)
        if not product_id:
            logger.error(f"Geçerli bir ürün ID'si bulunamadı: {url}")
            return {'success': False, 'error': 'Geçersiz ürün ID'}
        
        logger.info(f"Ürün bilgileri çekiliyor: ID {product_id}")
        
        # Önce API endpoint'ini dene
        result = self._try_api_endpoint(product_id)
        if result and result.get('success'):
            return result
        
        # API başarısız olursa HTML scraping dene
        if url.isdigit():
            # Sadece ID verilmişse, genel ürün URL'si oluştur
            product_url = f"https://www.trendyol.com/sr?q=&pi={product_id}"
        else:
            product_url = url
            
        result = self._try_html_scraping(product_url, product_id)
        return result if result else {'success': False, 'error': 'Ürün bilgileri alınamadı'}
    
    def _try_api_endpoint(self, product_id):
        """Trendyol API endpoint'ini dener."""
        api_urls = [
            f"https://public-mdc.trendyol.com/discovery-web-productdetailwidget-santral/api/v1/product-detail/{product_id}",
            f"https://public-mdc.trendyol.com/discovery-web-searchwidget-santral/api/v1/product/{product_id}",
        ]
        
        session = requests.Session()
        session.headers.update(self.headers)
        
        for api_url in api_urls:
            try:
                logger.info(f"API endpoint deneniyor: {api_url}")
                response = session.get(api_url, timeout=self.timeout, verify=self.verify_ssl)
                
                if response.status_code == 200:
                    data = response.json()
                    result = self._parse_api_response(data, product_id)
                    if result and result.get('success'):
                        logger.info("API endpoint'inden başarıyla veri alındı")
                        return result
                        
            except Exception as e:
                logger.warning(f"API endpoint hatası: {e}")
                continue
        
        return None
    
    def _parse_api_response(self, data, product_id):
        """API yanıtından ürün verilerini çıkarır."""
        try:
            # API yanıt yapısına göre veri çıkarma
            product_data = None
            
            # Farklı API yanıt formatlarını handle et
            if 'result' in data:
                product_data = data['result']
            elif 'product' in data:
                product_data = data['product']
            elif 'data' in data:
                product_data = data['data']
            else:
                product_data = data
            
            if not product_data:
                return None
            
            # Ürün bilgilerini çıkar
            name = product_data.get('name') or product_data.get('title') or product_data.get('productName')
            current_price = product_data.get('price', {}).get('discountedPrice') or product_data.get('currentPrice') or product_data.get('price')
            original_price = product_data.get('price', {}).get('originalPrice') or product_data.get('originalPrice') or current_price
            
            # Resim URL'si
            image_url = None
            images = product_data.get('images') or product_data.get('productImages') or []
            if images and len(images) > 0:
                image_url = images[0].get('url') or images[0]
                if image_url and not image_url.startswith('http'):
                    image_url = 'https:' + image_url
            
            # URL oluştur
            product_url = f"https://www.trendyol.com/sr?q=&pi={product_id}"
            
            if name and current_price is not None:
                return {
                    'product_id': product_id,
                    'name': name,
                    'url': product_url,
                    'image_url': image_url,
                    'current_price': float(current_price),
                    'original_price': float(original_price) if original_price else float(current_price),
                    'success': True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"API yanıtı parse edilirken hata: {e}")
            return None
    
    def _try_html_scraping(self, product_url, product_id):
        """HTML scraping ile ürün bilgilerini çekmeyi dener."""
        session = requests.Session()
        session.headers.update(self.headers)
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"HTML scraping deneniyor... (Deneme {attempt + 1}/{self.max_retries})")
                
                # Ana sayfaya git (bot korumasını aşmak için)
                if attempt == 0:
                    try:
                        session.get("https://www.trendyol.com", timeout=self.timeout, verify=self.verify_ssl)
                        time.sleep(1)
                    except:
                        pass
                
                response = session.get(product_url, timeout=self.timeout, verify=self.verify_ssl)
                response.raise_for_status()
                
                result = self._extract_html_data(response, product_url, product_id)
                if result and result.get('success'):
                    return result
                    
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"HTML scraping hatası (Deneme {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(3)
                continue
            except Exception as e:
                logger.error(f"HTML scraping genel hatası: {e}")
                break
        
        return None
    
    def _extract_html_data(self, response, product_url, product_id):
        """HTML yanıtından ürün verilerini çıkarır."""
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # JSON-LD structured data'yı ara
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    json_data = json.loads(script.string)
                    if json_data.get('@type') == 'Product':
                        return self._parse_json_ld(json_data, product_id, product_url)
                except:
                    continue
            
            # Window.__INITIAL_STATE__ veya benzeri JS değişkenlerini ara
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and ('__INITIAL_STATE__' in script.string or 'window.TYPageInfo' in script.string):
                    try:
                        # JS objesinden veri çıkarmaya çalış
                        script_content = script.string
                        # Bu kısım Trendyol'un JS yapısına göre özelleştirilmeli
                        # Şimdilik basit regex ile dene
                        
                        # Ürün adı
                        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', script_content)
                        price_match = re.search(r'"price"\s*:\s*(\d+\.?\d*)', script_content)
                        
                        if name_match and price_match:
                            return {
                                'product_id': product_id,
                                'name': name_match.group(1),
                                'url': product_url,
                                'image_url': None,
                                'current_price': float(price_match.group(1)),
                                'original_price': float(price_match.group(1)),
                                'success': True
                            }
                    except:
                        continue
            
            # Fallback: HTML elementlerinden çıkarmaya çalış
            return self._extract_from_html_elements(soup, product_id, product_url)
            
        except Exception as e:
            logger.error(f"HTML veri çıkarma hatası: {e}")
            return None
    
    def _parse_json_ld(self, json_data, product_id, product_url):
        """JSON-LD structured data'dan ürün bilgilerini çıkarır."""
        try:
            name = json_data.get('name')
            offers = json_data.get('offers', {})
            
            current_price = offers.get('price') or offers.get('lowPrice')
            original_price = offers.get('highPrice') or current_price
            
            image_url = None
            images = json_data.get('image')
            if images:
                if isinstance(images, list) and len(images) > 0:
                    image_url = images[0]
                elif isinstance(images, str):
                    image_url = images
            
            if name and current_price:
                return {
                    'product_id': product_id,
                    'name': name,
                    'url': product_url,
                    'image_url': image_url,
                    'current_price': float(current_price),
                    'original_price': float(original_price) if original_price else float(current_price),
                    'success': True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"JSON-LD parse hatası: {e}")
            return None
    
    def _extract_from_html_elements(self, soup, product_id, product_url):
        """HTML elementlerinden ürün bilgilerini çıkarır."""
        try:
            # Ürün adı
            product_name = None
            name_selectors = [
                'h1[data-testid="pdp-product-name"]',
                'h1.pr-new-br span',
                'h1.pr-new-br', 
                'h1[data-testid="product-name"]',
                'h1.product-name',
                '.pr-in-nm',
                '.pdp-product-name',
                'h1',
                '.product-detail-summary h1',
                '.product-name-price h1'
            ]
            
            for selector in name_selectors:
                try:
                    element = soup.select_one(selector)
                    if element and element.text.strip():
                        product_name = element.text.strip()
                        break
                except:
                    continue
            
            # Fiyat
            current_price = None
            price_selectors = [
                '[data-testid="price-current-price"]',
                '.prc-dsc',
                '.prc-slg', 
                '.product-price-container .prc-dsc',
                '.price-current',
                '.pdp-price .prc-dsc',
                '.price-box .prc-dsc',
                '.product-price .prc-dsc',
                'span[class*="price"]',
                '.current-price'
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = soup.select_one(selector)
                    if price_elem:
                        price_text = price_elem.text.strip()
                        current_price = self._parse_price(price_text)
                        if current_price is not None:
                            break
                except:
                    continue
            
            # Resim
            image_url = None
            image_selectors = [
                'img[data-testid="pdp-main-image"]',
                'img[data-testid="product-image"]',
                'img.ph-gl-img',
                '.product-slide img',
                '.gallery-modal img',
                '.pdp-image img',
                '.product-images img',
                'img[alt*="ürün"]',
                'img[src*="trendyol"]',
                '.image-viewer img'
            ]
            
            for selector in image_selectors:
                try:
                    img_elem = soup.select_one(selector)
                    if img_elem:
                        src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-original')
                        if src:
                            if not src.startswith('http'):
                                image_url = 'https:' + src
                            else:
                                image_url = src
                            break
                except:
                    continue
            
            if product_name and current_price is not None:
                return {
                    'product_id': product_id,
                    'name': product_name,
                    'url': product_url,
                    'image_url': image_url,
                    'current_price': current_price,
                    'original_price': current_price,
                    'success': True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"HTML element çıkarma hatası: {e}")
            return None
    
    def _parse_price(self, price_text):
        """Fiyat metnini sayıya çevirir."""
        try:
            if not price_text:
                return None
            
            # TL, ₺ gibi para birimlerini kaldır
            price_text = re.sub(r'(TL|₺|tl)', '', price_text, flags=re.IGNORECASE).strip()
            
            # Sadece sayıları, virgül ve noktaları bırak
            price_clean = re.sub(r'[^\d,.]', '', price_text)
            
            if not price_clean:
                return None
            
            # Türkçe format handling
            if ',' in price_clean and '.' in price_clean:
                comma_pos = price_clean.rfind(',')
                dot_pos = price_clean.rfind('.')
                
                if comma_pos > dot_pos:
                    # 1.234,56 format
                    integer_part = price_clean[:comma_pos].replace('.', '').replace(',', '')
                    decimal_part = price_clean[comma_pos+1:]
                    if len(decimal_part) <= 2:
                        price_clean = f"{integer_part}.{decimal_part}"
                    else:
                        price_clean = price_clean.replace(',', '')
                else:
                    # 1,234.56 format
                    integer_part = price_clean[:dot_pos].replace('.', '').replace(',', '')
                    decimal_part = price_clean[dot_pos+1:]
                    if len(decimal_part) <= 2:
                        price_clean = f"{integer_part}.{decimal_part}"
                    else:
                        price_clean = price_clean.replace(',', '')
                        
            elif ',' in price_clean:
                parts = price_clean.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    price_clean = price_clean.replace(',', '.')
                else:
                    price_clean = price_clean.replace(',', '')
            
            result = float(price_clean)
            
            if 0.01 <= result <= 1000000:
                return result
            else:
                logger.warning(f"Fiyat mantıksız aralıkta: {result}")
                return None
            
        except (ValueError, AttributeError) as e:
            logger.error(f"Fiyat parsing hatası: '{price_text}' -> {e}")
            return None
    
    def is_valid_url(self, url):
        """URL'nin Trendyol URL'si olup olmadığını kontrol eder."""
        if url.isdigit():
            return True
            
        try:
            parsed_url = urlparse(url)
            return "trendyol.com" in parsed_url.netloc
        except:
            return False