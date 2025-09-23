# config.py
# Configuration file for Trendyol scraper

# User Agent for web requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'

# Request configuration
MAX_RETRIES = 3
BACKOFF_FACTOR = 2
TIMEOUT = 15
MIN_DELAY = 1
MAX_DELAY = 3

# Price limits
MIN_PRICE = 0.01
MAX_PRICE = 100000

# Supported domains
TRENDYOL_DOMAINS = [
    'trendyol.com',
    'ty.gl',           # Mobil kısaltılmış linkler
    'tyml.gl',         # Trendyol Milla kısaltılmış linkler
    'trendyol-milla.com'
]

# URL patterns
TRENDYOL_URL_PATTERNS = [
    r'https?://(www\.)?trendyol\.com/.*-p-(\d+)',  # Normal ürün linki
    r'https?://ty\.gl/[a-zA-Z0-9]+',              # Mobil kısaltılmış link
    r'https?://tyml\.gl/[a-zA-Z0-9]+',            # Milla kısaltılmış link
    r'https?://(www\.)?trendyol\.com/sr\?.*pi=(\d+)',  # Arama linki
]

# Global Admin IDs (from environment or default)
import os
GLOBAL_ADMIN_IDS = os.getenv('GLOBAL_ADMIN_IDS', '992809942383870002,831185933117423656').split(',')