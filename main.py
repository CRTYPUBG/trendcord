import discord
from discord.ext import commands, tasks
import asyncio
import os
import logging
import dotenv
from datetime import datetime
import traceback
import ssl
import aiohttp
import urllib3

from database import Database
from scraper import TrendyolScraper

# .env dosyasını yükle
dotenv.load_dotenv()

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot ayarları
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX', '!')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 3600))  # Varsayılan olarak her saatte bir
PROXY_ENABLED = os.getenv('PROXY_ENABLED', 'True').lower() == 'true'
VERIFY_SSL = os.getenv('VERIFY_SSL', 'True').lower() == 'true'  # SSL doğrulama ayarı

# Veritabanı ayarları
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/trendyol_tracker.sqlite')
BACKUP_DATABASE_PATH = os.getenv('BACKUP_DATABASE_PATH', 'data/database.sqlite')

# SSL ayarı False ise SSL doğrulamasını devre dışı bırak
if not VERIFY_SSL:
    # SSL uyarılarını devre dışı bırak
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # SSL bağlantısı için özel context oluştur
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Özel HTTP oturumu oluştur
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    discord.http.HTTPClient.DEFAULT_CONNECTOR = connector
    
    logger.info("SSL sertifika doğrulaması devre dışı bırakıldı.")

# Bot oluşturma
intents = discord.Intents.default()
intents.message_content = True  # Mesaj içeriklerine erişim için

bot = commands.Bot(command_prefix=PREFIX, intents=intents, case_insensitive=True, help_command=None)

# Veritabanı ve scraper başlatma
db = Database(db_name=DATABASE_PATH)
scraper = TrendyolScraper(use_proxy=PROXY_ENABLED, verify_ssl=VERIFY_SSL)

@bot.event
async def on_ready():
    logger.info(f'Bot {bot.user.name} olarak giriş yaptı')
    logger.info(f'Bot ID: {bot.user.id}')
    
    # Cogları yükle
    await load_cogs()
    
    # Fiyat kontrolünü başlat
    if not check_prices.is_running():
        check_prices.start()
        logger.info(f"Fiyat kontrolü başlatıldı. Kontrol aralığı: {CHECK_INTERVAL} saniye")

async def load_cogs():
    """Tüm cogları yükler."""
    cogs_dir = os.path.abspath("cogs")
    
    # Cogs klasörü yoksa oluştur
    if not os.path.exists(cogs_dir):
        os.makedirs(cogs_dir)
        logger.info(f"Cogs klasörü oluşturuldu: {cogs_dir}")
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                logger.info(f"Cog yüklendi: {cog_name}")
            except Exception as e:
                logger.error(f"Cog yüklenirken hata: {cog_name}")
                logger.error(f"Hata: {e}")
                traceback.print_exc()

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_prices():
    """Takip edilen ürünlerin fiyatlarını kontrol eder."""
    logger.info("Fiyat kontrolü başlıyor...")
    
    # Tüm ürünleri al
    products = db.get_all_products()
    
    if not products:
        logger.info("Takip edilen ürün bulunamadı.")
        return
        
    logger.info(f"Toplam {len(products)} ürün kontrol edilecek.")
    
    for product in products:
        try:
            # Ürün bilgilerini çek
            product_data = scraper.scrape_product(product['url'])
            
            if not product_data or not product_data.get('success', False):
                logger.warning(f"Ürün bilgileri alınamadı: {product['product_id']} - {product['name']}")
                continue
                
            # Fiyat değişti mi kontrol et
            old_price = product['current_price']
            new_price = product_data['current_price']
            
            # Fiyatı güncelle
            db.update_product_price(product['product_id'], new_price)
            
            # Fiyat değişimi varsa bildirim gönder
            if old_price != new_price:
                try:
                    # Bildirimi gönderilecek kanalı bul
                    channel = bot.get_channel(int(product['channel_id']))
                    
                    if channel:
                        # Fiyat değişim embed'i oluştur
                        embed = discord.Embed(
                            title="💸 Fiyat Değişimi Bildirimi",
                            url=product['url'],
                            color=discord.Color.green() if new_price < old_price else discord.Color.red()
                        )
                        
                        embed.set_author(name=product['name'])
                        
                        if product['image_url']:
                            embed.set_thumbnail(url=product['image_url'])
                            
                        # Fiyat değişim bilgileri
                        price_diff = new_price - old_price
                        percentage = abs(price_diff / old_price * 100)
                        
                        if price_diff < 0:
                            change_text = f"🔽 **Fiyat Düştü!**\n{old_price:.2f} TL ➡️ {new_price:.2f} TL\n📉 {abs(price_diff):.2f} TL düşüş (-%{percentage:.1f})"
                        else:
                            change_text = f"🔼 **Fiyat Arttı!**\n{old_price:.2f} TL ➡️ {new_price:.2f} TL\n📈 {price_diff:.2f} TL artış (+%{percentage:.1f})"
                            
                        embed.description = change_text
                        
                        # Kullanıcı etiketi ekle
                        user_mention = f"<@{product['user_id']}>"
                        
                        # Bildirim gönder
                        await channel.send(content=f"{user_mention} takip ettiğin ürünün fiyatı değişti!", embed=embed)
                        logger.info(f"Fiyat değişimi bildirimi gönderildi: {product['name']}")
                    else:
                        logger.warning(f"Bildirim kanalı bulunamadı: {product['channel_id']}")
                        
                except Exception as e:
                    logger.error(f"Bildirim gönderilirken hata: {e}")
            
            # İşlemler arasında biraz bekle (rate limit'e takılmamak için)
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Ürün kontrolünde hata: {product['product_id']} - {e}")
            continue
    
    logger.info("Fiyat kontrolü tamamlandı.")

@check_prices.before_loop
async def before_check_prices():
    """Fiyat kontrolü başlamadan önce botun hazır olmasını bekler."""
    await bot.wait_until_ready()

@bot.event
async def on_command_error(ctx, error):
    """Komut hataları için hata mesajlarını işler."""
    if isinstance(error, commands.CommandNotFound):
        return
        
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Eksik argüman: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Geçersiz argüman tipi: {error}")
    else:
        logger.error(f"Komut hatası: {error}")
        await ctx.send(f"❌ Bir hata oluştu: {error}")

@bot.command(name="yardım", aliases=["yardim"])
async def custom_help(ctx):
    """Bot komutları hakkında yardım bilgisi verir."""
    embed = discord.Embed(
        title="📚 Trendyol Takip Botu - Yardım",
        description="Aşağıda kullanabileceğiniz komutların listesi bulunmaktadır.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name=f"{PREFIX}ekle <Trendyol Linki>",
        value="Takip edilecek ürün ekler. Fiyat değiştiğinde bildirim gönderilir.",
        inline=False
    )
    
    embed.add_field(
        name=f"{PREFIX}takiptekiler",
        value="Takip edilen ürünleri listeler.",
        inline=False
    )
    
    embed.add_field(
        name=f"{PREFIX}bilgi <Ürün ID veya URL>",
        value="Belirtilen ürün hakkında detaylı bilgi verir.",
        inline=False
    )
    
    embed.add_field(
        name=f"{PREFIX}sil <Ürün ID>",
        value="Takip edilen bir ürünü listeden çıkarır.",
        inline=False
    )
    
    embed.add_field(
        name=f"{PREFIX}güncelle <Ürün ID>",
        value="Ürün bilgilerini manuel olarak günceller.",
        inline=False
    )
    
    embed.add_field(
        name=f"{PREFIX}yardım",
        value="Bu yardım mesajını gösterir.",
        inline=False
    )
    
    embed.set_footer(text=f"Trendyol Takip Botu • Fiyat kontrol aralığı: {CHECK_INTERVAL//60} dakika")
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    # Discord token kontrolü
    if not TOKEN:
        logger.error("Discord token bulunamadı! Lütfen .env dosyasına DISCORD_TOKEN ekleyin.")
        exit(1)
    
    try:
        # SSL doğrulamasını devre dışı bırakarak botu başlat
        logger.info("SSL sertifika doğrulaması devre dışı bırakılarak bot başlatılıyor...")
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Bot başlatılırken hata oluştu: {e}")
        logger.error("Alternatif yöntem deneniyor...")
        
        # Alternatif yöntem: Çevre değişkenlerini ayarla
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        
        try:
            bot.run(TOKEN)
        except Exception as final_e:
            logger.error(f"Alternatif yöntem de başarısız oldu: {final_e}")
            logger.error("Lütfen internet bağlantınızı kontrol edin ve tekrar deneyin.")
            exit(1)