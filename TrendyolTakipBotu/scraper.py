import requests
from bs4 import BeautifulSoup
import re
import random
import os
import time
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("trendyol_scraper")

# Kötü proxy'leri takip etmek için
bad_proxies = {}
BAD_PROXY_TIMEOUT = 30 * 60  # 30 dakika

def get_product_info(url, proxies=None):
    """
    Trendyol ürün URL'sinden ürün bilgilerini çeker.
    
    Args:
        url (str): Trendyol ürün URL'si
        proxies (dict, optional): Kullanılacak proxy. Default: None
    
    Returns:
        dict: Ürün bilgileri veya None (hata durumunda)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive'
    }
    
    try:
        logger.info(f"Ürün bilgisi çekiliyor: {url} {'(proxy ile)' if proxies else '(proxy olmadan)'}")
        
        # Proxy kullanarak veya kullanmadan istek yap
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()
        
        # Proxy başarılı olduysa kötü proxy listesinden çıkar
        if proxies and proxies.get('http') in bad_proxies:
            logger.info(f"Proxy başarılı: {proxies.get('http')}")
            del bad_proxies[proxies.get('http')]
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trendyol'un güncel HTML yapısına göre seçicileri güncelle
        # Not: Bu seçiciler değişebilir, Trendyol'un güncel yapısını kontrol et
        name_tag = soup.select_one('h1.pr-new-br')
        price_tag = soup.select_one('span.prc-dsc')
        
        # Alternatif seçiciler (farklı sayfalar için)
        if not name_tag:
            name_tag = soup.select_one('h1.product-name')
        
        if not price_tag:
            price_tag = soup.select_one('span.product-price')
            
        # Resim için
        image_tag = soup.select_one('img.product-image')
        if not image_tag:
            image_tag = soup.select_one('div.gallery-container img')
            
        name = name_tag.text.strip() if name_tag else None
        
        # Fiyat bilgisini temizle ve sayıya çevir
        price = None
        if price_tag:
            price_text = price_tag.text.strip()
            # Fiyat metninden TL ve diğer karakterleri kaldır
            price_text = price_text.replace('TL', '').replace('.', '').replace(',', '.').strip()
            try:
                price = float(price_text)
            except ValueError:
                logger.warning(f"Fiyat parse edilemedi: {price_text}")
        
        image_url = None
        if image_tag and 'src' in image_tag.attrs:
            image_url = image_tag['src']
        
        # Trendyol ID'yi URL'den çıkar
        match_id = re.search(r'-p-(\d+)', url)
        trendyol_id = match_id.group(1) if match_id else None
        
        # Gerekli bilgilerin hepsi alındı mı kontrol et
        if not trendyol_id or not name or price is None:
            missing = []
            if not trendyol_id: missing.append("trendyol_id")
            if not name: missing.append("name")
            if price is None: missing.append("price")
            
            logger.error(f"Eksik ürün bilgileri: {', '.join(missing)} - URL: {url}")
            return None
        
        logger.info(f"Ürün bilgileri başarıyla çekildi: {name}, {price} TL")
        
        return {
            'trendyol_id': trendyol_id,
            'name': name,
            'price': price,
            'image_url': image_url,
            'url': url
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP istek hatası: {e} (URL: {url})")
        
        # Proxy hatalıysa kaydedelim
        if proxies and proxies.get('http'):
            proxy_address = proxies.get('http')
            bad_proxies[proxy_address] = time.time()
            logger.warning(f"Kötü proxy listesine eklendi: {proxy_address}")
            
        return None
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e} (URL: {url})", exc_info=True)
        return None

def load_proxies(file_path="proxies.txt"):
    """
    Proxy dosyasından proxy listesini yükler.
    
    Args:
        file_path (str): Proxy dosyasının yolu
    
    Returns:
        list: Proxy listesi
    """
    proxies = []
    
    if not os.path.exists(file_path):
        logger.warning(f"Proxy dosyası bulunamadı: {file_path}")
        return proxies
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    proxies.append(line)
        
        logger.info(f"{len(proxies)} proxy yüklendi: {file_path}")
        return proxies
    except Exception as e:
        logger.error(f"Proxy dosyası okuma hatası: {e}")
        return []

def clean_bad_proxies():
    """
    Belirli bir süre geçmiş kötü proxy'leri temizler.
    """
    current_time = time.time()
    to_remove = []
    
    for proxy, timestamp in bad_proxies.items():
        if current_time - timestamp > BAD_PROXY_TIMEOUT:
            to_remove.append(proxy)
    
    for proxy in to_remove:
        del bad_proxies[proxy]
        logger.info(f"Süre dolduğu için kötü proxy listesinden çıkarıldı: {proxy}")

def get_random_proxy(proxy_list):
    """
    Proxy listesinden rastgele ve geçerli bir proxy seçer.
    
    Args:
        proxy_list (list): Proxy listesi
    
    Returns:
        dict: Request için uygun formatta proxy, veya None
    """
    if not proxy_list:
        return None
    
    # Kötü proxy listesini temizle
    clean_bad_proxies()
    
    # Kötü proxy listesinde olmayan proxy'leri filtrele
    good_proxies = [p for p in proxy_list if f"http://{p}" not in bad_proxies]
    
    if not good_proxies:
        logger.warning("Kullanılabilir iyi proxy kalmadı!")
        # Alternatif olarak tüm listeyi kullanabiliriz, ancak bu durumda performans düşer
        if proxy_list:
            logger.info("Tüm proxy'ler kötü durumda, yine de biri seçiliyor...")
            proxy = random.choice(proxy_list)
        else:
            return None
    else:
        proxy = random.choice(good_proxies)
    
    return {
        'http': f'http://{proxy}',
        'https': f'https://{proxy}'
    } 