import discord
from discord.ext import commands
import asyncio
import re
import os
import sys

# Ana dizini import path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from scraper import TrendyolScraper
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.scraper = TrendyolScraper(use_proxy=True)
    
    @commands.command(name="ekle")
    async def add_product(self, ctx, url=None):
        """
        Takip edilecek ürün ekler.
        
        Kullanım:
            !ekle <Trendyol Linki>
        """
        if not url:
            await ctx.send("❌ Lütfen bir Trendyol ürün URL'si girin. Örnek: `!ekle https://www.trendyol.com/...`")
            return
        
        # URL'nin geçerli olup olmadığını kontrol et
        if not self.scraper.is_valid_url(url):
            await ctx.send("❌ Geçersiz Trendyol URL'si. Lütfen geçerli bir Trendyol ürün linki girin.")
            return
        
        # Yükleniyor mesajı
        loading_msg = await ctx.send("⏳ Ürün bilgileri alınıyor, lütfen bekleyin...")
        
        # Ürün bilgilerini çek
        product_data = self.scraper.scrape_product(url)
        
        if not product_data or not product_data.get('success', False):
            await loading_msg.edit(content="❌ Ürün bilgileri alınamadı. Lütfen URL'yi kontrol edin veya daha sonra tekrar deneyin.")
            return
        
        # Ürünü veritabanına ekle
        if self.db.add_product(product_data, str(ctx.guild.id), str(ctx.author.id), str(ctx.channel.id)):
            # Başarı embed'i oluştur
            embed = discord.Embed(
                title="✅ Ürün Takibe Alındı",
                description=f"**{product_data['name']}** artık takip listesinde!",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Ürün ID", value=product_data['product_id'], inline=True)
            embed.add_field(name="Mevcut Fiyat", value=f"{product_data['current_price']:.2f} TL", inline=True)
            
            if product_data['original_price'] and product_data['original_price'] != product_data['current_price']:
                embed.add_field(name="Normal Fiyat", value=f"{product_data['original_price']:.2f} TL", inline=True)
                
                # İndirim oranı hesapla
                discount_rate = ((product_data['original_price'] - product_data['current_price']) / product_data['original_price']) * 100
                embed.add_field(name="İndirim Oranı", value=f"%{discount_rate:.1f}", inline=True)
            
            embed.add_field(name="Ürün URL", value=f"[Trendyol'da Görüntüle]({product_data['url']})", inline=False)
            
            if product_data['image_url']:
                embed.set_thumbnail(url=product_data['image_url'])
                
            embed.set_footer(text=f"Ekleyen: {ctx.author.name} • Fiyat değiştiğinde bu kanala bildirim gönderilecek.")
            
            await loading_msg.edit(content=None, embed=embed)
        else:
            await loading_msg.edit(content="❌ Bu ürün zaten takip listenizde bulunuyor!")
    
    @commands.command(name="takiptekiler", aliases=["liste", "list"])
    async def list_products(self, ctx):
        """
        Takip edilen ürünleri listeler.
        
        Kullanım:
            !takiptekiler
        """
        # Kullanıcının takip ettiği ürünleri getir
        products = self.db.get_all_products(guild_id=str(ctx.guild.id))
        
        if not products:
            await ctx.send("📋 Takip edilen ürün bulunmuyor. Ürün eklemek için `!ekle <Trendyol Linki>` komutunu kullanın.")
            return
        
        # Ürünleri göstermek için bir embed oluştur
        embed = discord.Embed(
            title="📋 Takip Edilen Ürünler",
            description=f"Bu sunucuda toplam **{len(products)}** ürün takip ediliyor.",
            color=discord.Color.blue()
        )
        
        # Sayfalar için ürünleri grupla (her sayfada 5 ürün)
        items_per_page = 5
        pages = [products[i:i + items_per_page] for i in range(0, len(products), items_per_page)]
        current_page = 0
        total_pages = len(pages)
        
        # Sayfalama fonksiyonu
        async def update_embed():
            embed.clear_fields()
            embed.set_footer(text=f"Sayfa {current_page+1}/{total_pages} • Toplam {len(products)} ürün")
            
            for product in pages[current_page]:
                # Ürünü ekleyen kullanıcıyı bul
                user = None
                try:
                    user = await self.bot.fetch_user(int(product['user_id']))
                    user_name = user.name
                except:
                    user_name = "Bilinmiyor"
                
                value = f"💰 **Fiyat:** {product['current_price']:.2f} TL\n"
                value += f"🔗 [Trendyol'da Görüntüle]({product['url']})\n"
                value += f"👤 Ekleyen: {user_name}"
                
                embed.add_field(
                    name=f"📦 {product['name'][:50] + '...' if len(product['name']) > 50 else product['name']}",
                    value=value,
                    inline=False
                )
        
        await update_embed()
        message = await ctx.send(embed=embed)
        
        # Tek bir sayfa varsa reaksiyon eklemeye gerek yok
        if total_pages <= 1:
            return
        
        # Reaksiyonları ekle
        reactions = ['⬅️', '➡️']
        for reaction in reactions:
            await message.add_reaction(reaction)
            
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reactions and reaction.message.id == message.id
            
        # Reaksiyon loop
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                
                if str(reaction.emoji) == '➡️' and current_page < total_pages - 1:
                    current_page += 1
                    await update_embed()
                    await message.edit(embed=embed)
                    
                elif str(reaction.emoji) == '⬅️' and current_page > 0:
                    current_page -= 1
                    await update_embed()
                    await message.edit(embed=embed)
                    
                await message.remove_reaction(reaction.emoji, user)
                
            except asyncio.TimeoutError:
                break
    
    @commands.command(name="bilgi", aliases=["info"])
    async def product_info(self, ctx, product_identifier=None):
        """
        Ürün hakkında detaylı bilgi verir.
        
        Kullanım:
            !bilgi <Ürün ID veya URL>
        """
        if not product_identifier:
            await ctx.send("❌ Lütfen bir ürün ID'si veya URL'si girin. Örnek: `!bilgi 12345678` veya `!bilgi https://www.trendyol.com/...`")
            return
        
        # URL ise ürün ID'sini çıkar
        product_id = product_identifier
        if not product_identifier.isdigit():
            product_id = self.scraper.extract_product_id(product_identifier)
            
        if not product_id:
            await ctx.send("❌ Geçerli bir ürün ID'si veya URL'si bulunamadı.")
            return
        
        # Ürün bilgilerini getir
        product = self.db.get_product(product_id)
        
        if not product:
            # Eğer veritabanında yoksa, ürünü çek ama kaydetme
            loading_msg = await ctx.send("⏳ Ürün bilgileri alınıyor, lütfen bekleyin...")
            product_data = self.scraper.scrape_product(product_identifier)
            
            if not product_data or not product_data.get('success', False):
                await loading_msg.edit(content="❌ Ürün bilgileri alınamadı. Lütfen URL'yi kontrol edin veya daha sonra tekrar deneyin.")
                return
                
            embed = discord.Embed(
                title=product_data['name'],
                description="⚠️ Bu ürün henüz takip listenizde değil. Takip etmek için `!ekle` komutunu kullanın.",
                color=discord.Color.gold()
            )
            
            embed.add_field(name="Ürün ID", value=product_data['product_id'], inline=True)
            embed.add_field(name="Mevcut Fiyat", value=f"{product_data['current_price']:.2f} TL", inline=True)
            
            if product_data['original_price'] and product_data['original_price'] != product_data['current_price']:
                embed.add_field(name="Normal Fiyat", value=f"{product_data['original_price']:.2f} TL", inline=True)
                
                # İndirim oranı hesapla
                discount_rate = ((product_data['original_price'] - product_data['current_price']) / product_data['original_price']) * 100
                embed.add_field(name="İndirim Oranı", value=f"%{discount_rate:.1f}", inline=True)
            
            embed.add_field(name="Ürün URL", value=f"[Trendyol'da Görüntüle]({product_data['url']})", inline=False)
            
            if product_data['image_url']:
                embed.set_thumbnail(url=product_data['image_url'])
                
            await loading_msg.edit(content=None, embed=embed)
            return
        
        # Fiyat geçmişini al
        price_history = self.db.get_price_history(product_id)
        
        # Kullanıcı bilgisini al
        user = None
        try:
            user = await self.bot.fetch_user(int(product['user_id']))
            user_name = user.name
        except:
            user_name = "Bilinmiyor"
        
        # Embed oluştur
        embed = discord.Embed(
            title=product['name'],
            description=f"Bu ürün **{user_name}** tarafından takip listesine eklendi.",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Ürün ID", value=product['product_id'], inline=True)
        embed.add_field(name="Mevcut Fiyat", value=f"{product['current_price']:.2f} TL", inline=True)
        
        if product['original_price'] and product['original_price'] != product['current_price']:
            embed.add_field(name="Normal Fiyat", value=f"{product['original_price']:.2f} TL", inline=True)
            
            # İndirim oranı hesapla
            discount_rate = ((product['original_price'] - product['current_price']) / product['original_price']) * 100
            embed.add_field(name="İndirim Oranı", value=f"%{discount_rate:.1f}", inline=True)
        
        # En düşük, en yüksek ve ortalama fiyatı hesapla
        if price_history:
            prices = [item['price'] for item in price_history]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            
            embed.add_field(name="En Düşük Fiyat", value=f"{min_price:.2f} TL", inline=True)
            embed.add_field(name="En Yüksek Fiyat", value=f"{max_price:.2f} TL", inline=True)
            embed.add_field(name="Ortalama Fiyat", value=f"{avg_price:.2f} TL", inline=True)
            
            # Son fiyat değişimi
            if len(price_history) > 1:
                last_price = price_history[0]['price']
                prev_price = price_history[1]['price']
                price_change = last_price - prev_price
                
                if price_change != 0:
                    change_text = f"{'-' if price_change < 0 else '+'}{abs(price_change):.2f} TL"
                    embed.add_field(name="Son Fiyat Değişimi", value=change_text, inline=True)
        
        embed.add_field(name="Ürün URL", value=f"[Trendyol'da Görüntüle]({product['url']})", inline=False)
        embed.add_field(name="Eklenme Tarihi", value=product['added_at'].split('T')[0], inline=True)
        embed.add_field(name="Son Kontrol", value=product['last_checked'].split('T')[0], inline=True)
        
        if product['image_url']:
            embed.set_thumbnail(url=product['image_url'])
            
        await ctx.send(embed=embed)
    
    @commands.command(name="sil", aliases=["delete", "remove"])
    async def delete_product(self, ctx, product_id=None):
        """
        Takip edilen bir ürünü siler.
        
        Kullanım:
            !sil <Ürün ID>
        """
        if not product_id:
            await ctx.send("❌ Lütfen silmek istediğiniz ürünün ID'sini girin. Örnek: `!sil 12345678`")
            return
        
        # Ürün URL'si girilmişse ID'yi çıkar
        if not product_id.isdigit():
            product_id = self.scraper.extract_product_id(product_id)
            
        if not product_id:
            await ctx.send("❌ Geçerli bir ürün ID'si bulunamadı.")
            return
        
        # Ürünün var olduğunu kontrol et
        product = self.db.get_product(product_id)
        
        if not product:
            await ctx.send("❌ Bu ID'ye sahip bir ürün bulunamadı. Takip ettiğiniz ürünleri görmek için `!takiptekiler` komutunu kullanın.")
            return
        
        # Kullanıcı yetkili mi kontrol et (ürünü ekleyen kişi veya yönetici)
        if str(ctx.author.id) != product['user_id'] and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Bu ürünü silmek için yetkiniz yok. Sadece ürünü ekleyen kişi veya sunucu yöneticileri silebilir.")
            return
        
        # Onay iste
        confirm_msg = await ctx.send(f"⚠️ **{product['name']}** adlı ürünü takip listesinden silmek istediğinize emin misiniz? Onaylamak için 👍 emojisine tıklayın.")
        await confirm_msg.add_reaction("👍")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "👍" and reaction.message.id == confirm_msg.id
            
        try:
            await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            # Ürünü sil
            if self.db.delete_product(product_id, str(ctx.guild.id), str(ctx.author.id)):
                await ctx.send(f"✅ **{product['name']}** adlı ürün takip listesinden silindi.")
            else:
                await ctx.send("❌ Ürün silinirken bir hata oluştu.")
                
        except asyncio.TimeoutError:
            await ctx.send("⏱️ Onay zaman aşımına uğradı. Ürün silinmedi.")
    
    @commands.command(name="güncelle", aliases=["update"])
    async def update_product(self, ctx, product_id=None):
        """
        Ürün bilgilerini günceller.
        
        Kullanım:
            !güncelle <Ürün ID>
        """
        if not product_id:
            await ctx.send("❌ Lütfen güncellemek istediğiniz ürünün ID'sini girin. Örnek: `!güncelle 12345678`")
            return
        
        # Ürün URL'si girilmişse ID'yi çıkar
        if not product_id.isdigit():
            product_id = self.scraper.extract_product_id(product_id)
            
        if not product_id:
            await ctx.send("❌ Geçerli bir ürün ID'si bulunamadı.")
            return
        
        # Ürünün var olduğunu kontrol et
        product = self.db.get_product(product_id)
        
        if not product:
            await ctx.send("❌ Bu ID'ye sahip bir ürün bulunamadı. Takip ettiğiniz ürünleri görmek için `!takiptekiler` komutunu kullanın.")
            return
        
        # Yükleniyor mesajı
        loading_msg = await ctx.send("⏳ Ürün bilgileri güncelleniyor, lütfen bekleyin...")
        
        # Ürün bilgilerini yeniden çek
        product_data = self.scraper.scrape_product(product['url'])
        
        if not product_data or not product_data.get('success', False):
            await loading_msg.edit(content="❌ Ürün bilgileri alınamadı. Lütfen daha sonra tekrar deneyin.")
            return
        
        # Fiyatı güncelle
        old_price = product['current_price']
        new_price = product_data['current_price']
        
        self.db.update_product_price(product_id, new_price)
        
        # Başarı mesajı
        embed = discord.Embed(
            title="✅ Ürün Güncellendi",
            description=f"**{product_data['name']}** adlı ürünün fiyatı güncellendi.",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Ürün ID", value=product_id, inline=True)
        embed.add_field(name="Eski Fiyat", value=f"{old_price:.2f} TL", inline=True)
        embed.add_field(name="Yeni Fiyat", value=f"{new_price:.2f} TL", inline=True)
        
        # Fiyat değişimi
        if old_price != new_price:
            price_diff = new_price - old_price
            if price_diff < 0:
                embed.add_field(name="Fiyat Değişimi", value=f"🔽 {abs(price_diff):.2f} TL düşüş (%{abs(price_diff / old_price * 100):.1f})", inline=False)
                embed.color = discord.Color.green()
            else:
                embed.add_field(name="Fiyat Değişimi", value=f"🔼 {price_diff:.2f} TL artış (%{price_diff / old_price * 100:.1f})", inline=False)
                embed.color = discord.Color.red()
        else:
            embed.add_field(name="Fiyat Değişimi", value="Fiyat değişmedi", inline=False)
            
        if product_data['image_url']:
            embed.set_thumbnail(url=product_data['image_url'])
            
        await loading_msg.edit(content=None, embed=embed)

async def setup(bot):
    await bot.add_cog(ProductCommands(bot)) 