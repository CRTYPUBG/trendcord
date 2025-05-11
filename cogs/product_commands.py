# cogs/product_commands.py

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from datetime import datetime # Tarih formatlama için
import logging

logger = logging.getLogger(__name__)

class ProductCommands(commands.Cog, name="Ürün Komutları"): # Cog'a isim verdik (yardım için)
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db # main.py'den gelen db instance'ı
        self.scraper = bot.scraper # main.py'den gelen scraper instance'ı

    # --- İÇ MANTIK FONKSİYONLARI ---

    async def _internal_add_product_logic(self, url: str, guild_id: str, user_id: str, channel_id: str):
        """Ürün ekleme işleminin temel mantığını içerir."""
        if not self.scraper.is_valid_url(url):
            return False, "❌ Geçersiz Trendyol URL'si. Lütfen geçerli bir Trendyol ürün linki girin."

        product_data = self.scraper.scrape_product(url)
        if not product_data or not product_data.get('success', False):
            return False, "❌ Ürün bilgileri alınamadı. Lütfen URL'yi kontrol edin veya daha sonra tekrar deneyin."
        
        if product_data.get('current_price') is None:
             return False, "❌ Ürün fiyat bilgisi alınamadı. Ürün stokta olmayabilir veya sayfa yapısı değişmiş olabilir."

        if self.db.add_product(product_data, guild_id, user_id, channel_id):
            return True, product_data
        else:
            # Bu ürün zaten takip listenizde olabilir veya veritabanı hatası olabilir.
            # get_product ile kontrol edip daha spesifik bir mesaj verilebilir.
            existing_product = self.db.get_product(product_data['product_id'])
            if existing_product and str(existing_product.get('guild_id')) == guild_id : # Aynı sunucuda mı?
                 return False, "❌ Bu ürün zaten bu sunucuda takip listenizde bulunuyor!"
            return False, "❌ Ürün eklenirken bir hata oluştu veya bu ürün zaten genel takip listenizde mevcut."

    async def _internal_list_products_logic(self, guild_id: str):
        """Belirli bir sunucudaki takip edilen ürünleri listeler."""
        products = self.db.get_all_products(guild_id=guild_id)
        if not products:
            return False, "📋 Takip edilen ürün bulunmuyor."
        return True, products

    async def _internal_product_info_logic(self, product_identifier: str):
        """Ürün ID'si veya URL ile ürün bilgisi ve fiyat geçmişini getirir."""
        product_id = self.scraper.extract_product_id(product_identifier)
        if not product_id:
            return False, "❌ Geçerli bir ürün ID'si veya URL'si bulunamadı."

        product = self.db.get_product(product_id)
        if not product:
            # Veritabanında yoksa ve geçerli bir URL ise, anlık çekmeyi dene
            if self.scraper.is_valid_url(product_identifier):
                scraped_data = self.scraper.scrape_product(product_identifier)
                if scraped_data and scraped_data.get('success'):
                    return True, {"scraped_data": scraped_data, "not_tracked": True}
            return False, f"❌ ID'si `{product_id}` olan ürün veritabanında bulunamadı."

        price_history = self.db.get_price_history(product_id)
        return True, {"product": product, "price_history": price_history}

    async def _internal_delete_product_logic(self, product_identifier: str, guild_id: str, requesting_user_id: str, is_admin: bool):
        """Ürünü silme mantığı."""
        product_id = self.scraper.extract_product_id(product_identifier)
        if not product_id:
            return False, "❌ Geçerli bir ürün ID'si bulunamadı."

        product = self.db.get_product(product_id)
        if not product:
            return False, f"❌ ID'si `{product_id}` olan bir ürün takip listenizde bulunamadı."

        # Silinecek ürünün bu sunucuya ait olup olmadığını kontrol et (opsiyonel ama iyi bir pratik)
        if str(product.get('guild_id')) != guild_id:
            return False, f"❌ ID'si `{product_id}` olan ürün bu sunucuda takip edilmiyor."

        product_owner_id = product.get('user_id')
        if str(requesting_user_id) != product_owner_id and not is_admin:
            return False, "❌ Bu ürünü silmek için yetkiniz yok. Sadece ürünü ekleyen kişi veya sunucu yöneticileri silebilir."

        if self.db.delete_product(product_id, guild_id=guild_id): # Sadece bu guild için sil
            return True, product.get('name', 'İsimsiz Ürün')
        else:
            return False, f"❌ Ürün (`{product_id}`) silinirken bir hata oluştu."

    async def _internal_update_product_logic(self, product_identifier: str):
        """Ürün bilgilerini manuel güncelleme mantığı."""
        product_id = self.scraper.extract_product_id(product_identifier)
        if not product_id:
            return False, "❌ Geçerli bir ürün ID'si bulunamadı."

        product_db = self.db.get_product(product_id)
        if not product_db:
            return False, f"❌ ID'si `{product_id}` olan bir ürün takip listenizde bulunamadı."

        product_url = product_db.get('url')
        if not product_url:
            return False, f"❌ Ürünün (`{product_id}`) kayıtlı bir URL'si bulunamadı."

        new_data = self.scraper.scrape_product(product_url)
        if not new_data or not new_data.get('success', False):
            return False, f"❌ Ürün (`{product_id}`) bilgileri Trendyol'dan alınamadı."
        
        if new_data.get('current_price') is None:
            return False, f"❌ Yeni fiyat bilgisi alınamadı (`{product_id}`)."

        old_price = product_db.get('current_price')
        self.db.update_product_price(product_id, new_data['current_price'])
        return True, {"new_data": new_data, "old_price": old_price, "product_id": product_id}

    # --- EMBED OLUŞTURMA YARDIMCILARI ---
    def _create_product_added_embed(self, product_data, user_name, command_type=""):
        title_suffix = f" ({command_type})" if command_type else ""
        embed = discord.Embed(
            title=f"✅ Ürün Takibe Alındı{title_suffix}",
            description=f"**{product_data['name']}** artık takip listesinde!",
            color=discord.Color.green()
        )
        embed.add_field(name="Ürün ID", value=product_data['product_id'], inline=True)
        embed.add_field(name="Mevcut Fiyat", value=f"{product_data.get('current_price', 0):.2f} TL", inline=True)
        
        original_price = product_data.get('original_price')
        current_price = product_data.get('current_price')
        if original_price and current_price and original_price != current_price:
            embed.add_field(name="Normal Fiyat", value=f"{original_price:.2f} TL", inline=True)
            if original_price > 0:
                discount_rate = ((original_price - current_price) / original_price) * 100
                embed.add_field(name="İndirim Oranı", value=f"%{discount_rate:.1f}", inline=True)
        embed.add_field(name="Ürün URL", value=f"[Trendyol'da Görüntüle]({product_data['url']})", inline=False)
        if product_data.get('image_url'):
            embed.set_thumbnail(url=product_data['image_url'])
        embed.set_footer(text=f"Ekleyen: {user_name} • Fiyat değiştiğinde bildirim gönderilecek.")
        return embed

    def _create_product_info_embed(self, data, user_name_fetcher, command_type=""):
        title_suffix = f" ({command_type})" if command_type else ""
        if data.get("not_tracked"): # Anlık çekilen, takipte olmayan ürün
            scraped = data["scraped_data"]
            embed = discord.Embed(
                title=f"{scraped['name']}{title_suffix}",
                description="⚠️ Bu ürün henüz takip listenizde değil. Takip etmek için `/ekle` veya `!ekle` komutunu kullanın.",
                color=discord.Color.gold()
            )
            embed.add_field(name="Ürün ID", value=scraped['product_id'], inline=True)
            embed.add_field(name="Mevcut Fiyat", value=f"{scraped.get('current_price',0):.2f} TL", inline=True)
            if scraped.get('image_url'): embed.set_thumbnail(url=scraped['image_url'])
            return embed

        product = data["product"]
        price_history = data["price_history"]
        
        # user_name = "Bilinmiyor" # Bu async olmalı, embed içinde çağıramayız direkt
        # if product.get('user_id'):
        #     try: user = await self.bot.fetch_user(int(product['user_id'])); user_name = user.name
        #     except: pass
        # Bu kısmı handler'da yapıp embed fonksiyonuna user_name olarak vermek daha iyi.
        # Şimdilik "Ekleyen Bilgisi Yükleniyor" diyelim veya handler'dan alalım.
        # Bu fonksiyon sync olduğu için async fetch_user çağıramaz.
        # Bu nedenle user_name_fetcher'ı dışarıdan alacağız (bir coroutine).

        embed = discord.Embed(
            title=f"{product.get('name', 'İsimsiz Ürün')}{title_suffix}",
            # description=f"Bu ürün **{user_name}** tarafından takip listesine eklendi.", # user_name dışarıdan gelecek
            color=discord.Color.blue()
        )
        embed.add_field(name="Ürün ID", value=product['product_id'], inline=True)
        embed.add_field(name="Mevcut Fiyat", value=f"{product.get('current_price',0):.2f} TL", inline=True)
        
        original_price = product.get('original_price')
        current_price = product.get('current_price')
        if original_price and current_price and original_price != current_price:
            embed.add_field(name="Normal Fiyat", value=f"{original_price:.2f} TL", inline=True)
            if original_price > 0:
                discount_rate = ((original_price - current_price) / original_price) * 100
                embed.add_field(name="İndirim Oranı", value=f"%{discount_rate:.1f}", inline=True)
        
        if price_history:
            prices = [item['price'] for item in price_history if item.get('price') is not None]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                embed.add_field(name="En Düşük Fiyat", value=f"{min_price:.2f} TL", inline=True)
                embed.add_field(name="En Yüksek Fiyat", value=f"{max_price:.2f} TL", inline=True)
                embed.add_field(name="Ortalama Fiyat", value=f"{avg_price:.2f} TL", inline=True)
        
        embed.add_field(name="Ürün URL", value=f"[Trendyol'da Görüntüle]({product['url']})", inline=False)
        
        try: added_at_dt = datetime.fromisoformat(product['added_at']); embed.add_field(name="Eklenme Tarihi", value=added_at_dt.strftime("%d.%m.%Y"), inline=True)
        except: pass
        try: last_checked_dt = datetime.fromisoformat(product['last_checked']); embed.add_field(name="Son Kontrol", value=last_checked_dt.strftime("%d.%m.%Y %H:%M"), inline=True)
        except: pass

        if product.get('image_url'):
            embed.set_thumbnail(url=product['image_url'])

        history_text = ""
        if price_history:
            for entry in price_history[:5]:
                try:
                    dt_object = datetime.fromisoformat(entry['date'])
                    formatted_date = dt_object.strftime("%d.%m.%Y %H:%M")
                    history_text += f"- {formatted_date}: {entry.get('price', 0):.2f} TL\n"
                except:
                     history_text += f"- {entry.get('date','Bilinmeyen Tarih')}: {entry.get('price', 0):.2f} TL\n"
        embed.add_field(name="Fiyat Geçmişi (Son 5)", value=history_text if history_text else "Kayıt yok.", inline=False)
        return embed

    def _create_product_updated_embed(self, data, command_type=""):
        title_suffix = f" ({command_type})" if command_type else ""
        new_data = data["new_data"]
        old_price = data["old_price"]
        product_id = data["product_id"]

        embed = discord.Embed(
            title=f"✅ Ürün Güncellendi{title_suffix}",
            description=f"**{new_data.get('name', 'İsimsiz Ürün')}** (`{product_id}`) adlı ürünün fiyatı güncellendi.",
            color=discord.Color.green()
        )
        embed.add_field(name="Eski Fiyat", value=f"{old_price:.2f} TL" if old_price is not None else "Bilinmiyor", inline=True)
        embed.add_field(name="Yeni Fiyat", value=f"{new_data.get('current_price',0):.2f} TL", inline=True)
        
        current_price = new_data.get('current_price')
        if old_price is not None and current_price is not None and old_price != current_price:
            price_diff = current_price - old_price
            if old_price > 0:
                percentage_change = abs(price_diff / old_price * 100)
                change_direction = "düşüş" if price_diff < 0 else "artış"
                emoji = "🔽" if price_diff < 0 else "🔼"
                embed.add_field(name="Fiyat Değişimi", value=f"{emoji} {abs(price_diff):.2f} TL {change_direction} (%{percentage_change:.1f})", inline=False)
                embed.color = discord.Color.green() if price_diff < 0 else discord.Color.red()
        elif old_price is not None and current_price is not None and old_price == current_price:
             embed.add_field(name="Fiyat Değişimi", value="Fiyat değişmedi.", inline=False)
        if new_data.get('image_url'):
            embed.set_thumbnail(url=new_data['image_url'])
        return embed

    # --- PREFIX KOMUTLARI ---

    @commands.command(name="ekle", help="Takip edilecek Trendyol ürününü ekler. Kullanım: !ekle <URL>")
    @commands.guild_only()
    async def ekle_prefix(self, ctx: commands.Context, *, url: str = None):
        if not url:
            await ctx.send(f"❌ Lütfen bir Trendyol ürün URL'si girin. Örnek: `{self.bot.command_prefix}ekle https://www.trendyol.com/...`")
            return
        
        async with ctx.typing(): # Kullanıcıya işlem yapıldığını gösterir
            success, result = await self._internal_add_product_logic(
                url, str(ctx.guild.id), str(ctx.author.id), str(ctx.channel.id)
            )

        if success:
            product_data = result
            embed = self._create_product_added_embed(product_data, ctx.author.name, "Prefix")
            await ctx.send(embed=embed)
        else:
            await ctx.send(result) # Hata mesajı

    @commands.command(name="takiptekiler", aliases=["liste"], help="Bu sunucuda takip edilen ürünleri listeler.")
    @commands.guild_only()
    async def takiptekiler_prefix(self, ctx: commands.Context):
        async with ctx.typing():
            success, result = await self._internal_list_products_logic(str(ctx.guild.id))

        if not success: # Hata veya boş liste
            await ctx.send(result)
            return

        products = result
        embed = discord.Embed(
            title="📋 Takip Edilen Ürünler (Prefix)",
            description=f"Bu sunucuda toplam **{len(products)}** ürün takip ediliyor.",
            color=discord.Color.blue()
        )
        # Sayfalama eklenebilir, şimdilik ilk 10
        for i, product_db in enumerate(products[:10]):
            user_name = "Bilinmiyor"
            if product_db.get('user_id'):
                try: user = await self.bot.fetch_user(int(product_db['user_id'])); user_name = user.name
                except: pass
            value = f"🆔 **ID:** `{product_db['product_id']}`\n" \
                    f"💰 **Fiyat:** {product_db.get('current_price', 0):.2f} TL\n" \
                    f"🔗 [Trendyol]({product_db['url']})\n" \
                    f"👤 Ekleyen: {user_name}"
            embed.add_field(
                name=f"📦 {product_db.get('name', 'İsimsiz Ürün')[:50]}{'...' if len(product_db.get('name', '')) > 50 else ''}",
                value=value,
                inline=False
            )
        if len(products) > 10: embed.set_footer(text=f"Toplam {len(products)} ürünün ilk 10 tanesi gösteriliyor.")
        else: embed.set_footer(text=f"Toplam {len(products)} ürün.")
        await ctx.send(embed=embed)

    @commands.command(name="bilgi", help="Belirtilen ürün hakkında detaylı bilgi verir. Kullanım: !bilgi <ID veya URL>")
    async def bilgi_prefix(self, ctx: commands.Context, *, product_identifier: str = None):
        if not product_identifier:
            await ctx.send(f"❌ Lütfen bir ürün ID'si veya URL'si girin. Örnek: `{self.bot.command_prefix}bilgi <ID veya URL>`")
            return
        
        async with ctx.typing():
            success, result = await self._internal_product_info_logic(product_identifier)

        if not success:
            await ctx.send(result)
            return
        
        embed = self._create_product_info_embed(result, None, "Prefix") # user_name_fetcher'ı None verdik, embed içinde fetch edilecek
        
        # Embed'in description'ını güncelle (user_name için)
        user_name_for_embed = "Bilinmiyor"
        if not result.get("not_tracked") and result.get("product", {}).get("user_id"):
            try:
                user = await self.bot.fetch_user(int(result["product"]["user_id"]))
                user_name_for_embed = user.name
            except: pass
        
        if not result.get("not_tracked"):
             embed.description = f"Bu ürün **{user_name_for_embed}** tarafından takip listesine eklendi."
        
        await ctx.send(embed=embed)

    @commands.command(name="sil", help="Takip edilen bir ürünü listeden çıkarır. Kullanım: !sil <ID>")
    @commands.guild_only()
    async def sil_prefix(self, ctx: commands.Context, *, product_identifier: str = None):
        if not product_identifier:
            await ctx.send(f"❌ Lütfen silmek istediğiniz ürünün ID'sini veya URL'sini girin. Örnek: `{self.bot.command_prefix}sil <ID>`")
            return

        async with ctx.typing():
            success, result = await self._internal_delete_product_logic(
                product_identifier, str(ctx.guild.id), str(ctx.author.id), ctx.author.guild_permissions.administrator
            )
        
        if success:
            product_name = result
            await ctx.send(f"✅ **{product_name}** adlı ürün takip listesinden silindi.")
        else:
            await ctx.send(result)

    @commands.command(name="güncelle", aliases=["guncelle"], help="Ürün bilgilerini manuel olarak günceller. Kullanım: !güncelle <ID>")
    async def guncelle_prefix(self, ctx: commands.Context, *, product_identifier: str = None):
        if not product_identifier:
            await ctx.send(f"❌ Lütfen güncellemek istediğiniz ürünün ID'sini veya URL'sini girin. Örnek: `{self.bot.command_prefix}güncelle <ID>`")
            return

        async with ctx.typing():
            success, result = await self._internal_update_product_logic(product_identifier)

        if success:
            embed = self._create_product_updated_embed(result, "Prefix")
            await ctx.send(embed=embed)
        else:
            await ctx.send(result)

    # --- SLASH KOMUTLARI ---

    @app_commands.command(name="ekle", description="Takip edilecek Trendyol ürününü ekler.")
    @app_commands.describe(url="Takip edilecek Trendyol ürününün linki")
    @app_commands.guild_only()
    async def ekle_slash(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(thinking=True) # thinking=True daha iyi bir UX
        success, result = await self._internal_add_product_logic(
            url, str(interaction.guild.id), str(interaction.user.id), str(interaction.channel.id)
        )
        if success:
            product_data = result
            embed = self._create_product_added_embed(product_data, interaction.user.name, "Slash")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(result)

    @app_commands.command(name="takiptekiler", description="Bu sunucuda takip edilen ürünleri listeler.")
    @app_commands.guild_only()
    async def takiptekiler_slash(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        success, result = await self._internal_list_products_logic(str(interaction.guild.id))

        if not success:
            await interaction.followup.send(result)
            return
        
        products = result
        embed = discord.Embed(
            title="📋 Takip Edilen Ürünler (Slash)",
            description=f"Bu sunucuda toplam **{len(products)}** ürün takip ediliyor.",
            color=discord.Color.purple() # Farklı renk
        )
        for i, product_db in enumerate(products[:10]): # Sayfalama için butonlar eklenebilir
            user_name = "Bilinmiyor"
            if product_db.get('user_id'):
                try: user = await self.bot.fetch_user(int(product_db['user_id'])); user_name = user.name
                except: pass
            value = f"🆔 **ID:** `{product_db['product_id']}`\n" \
                    f"💰 **Fiyat:** {product_db.get('current_price', 0):.2f} TL\n" \
                    f"🔗 [Trendyol]({product_db['url']})\n" \
                    f"👤 Ekleyen: {user_name}"
            embed.add_field(
                name=f"📦 {product_db.get('name', 'İsimsiz Ürün')[:50]}{'...' if len(product_db.get('name', '')) > 50 else ''}",
                value=value,
                inline=False
            )
        if len(products) > 10: embed.set_footer(text=f"Toplam {len(products)} ürünün ilk 10 tanesi gösteriliyor.")
        else: embed.set_footer(text=f"Toplam {len(products)} ürün.")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="bilgi", description="Belirtilen ürün hakkında detaylı bilgi verir.")
    @app_commands.describe(urun_kimligi="Ürünün Trendyol ID'si veya URL'si")
    async def bilgi_slash(self, interaction: discord.Interaction, urun_kimligi: str):
        await interaction.response.defer(thinking=True)
        success, result = await self._internal_product_info_logic(urun_kimligi)

        if not success:
            await interaction.followup.send(result)
            return
            
        embed = self._create_product_info_embed(result, None, "Slash")
        user_name_for_embed = "Bilinmiyor"
        if not result.get("not_tracked") and result.get("product", {}).get("user_id"):
            try:
                user = await self.bot.fetch_user(int(result["product"]["user_id"]))
                user_name_for_embed = user.name
            except: pass
        
        if not result.get("not_tracked"):
             embed.description = f"Bu ürün **{user_name_for_embed}** tarafından takip listesine eklendi."

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="sil", description="Takip edilen bir ürünü listeden çıkarır.")
    @app_commands.describe(urun_kimligi="Silinecek ürünün Trendyol ID'si veya URL'si")
    @app_commands.guild_only()
    async def sil_slash(self, interaction: discord.Interaction, urun_kimligi: str):
        await interaction.response.defer(thinking=True)
        success, result = await self._internal_delete_product_logic(
            urun_kimligi, str(interaction.guild.id), str(interaction.user.id), interaction.user.guild_permissions.administrator
        )
        if success:
            product_name = result
            await interaction.followup.send(f"✅ **{product_name}** adlı ürün takip listesinden silindi.")
        else:
            await interaction.followup.send(result)

    @app_commands.command(name="guncelle", description="Ürün bilgilerini manuel olarak günceller.")
    @app_commands.describe(urun_kimligi="Güncellenecek ürünün Trendyol ID'si veya URL'si")
    async def guncelle_slash(self, interaction: discord.Interaction, urun_kimligi: str):
        await interaction.response.defer(thinking=True)
        success, result = await self._internal_update_product_logic(urun_kimligi)
        if success:
            embed = self._create_product_updated_embed(result, "Slash")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(result)

    @app_commands.command(name="yardim", description="Bot komutları hakkında yardım bilgisi verir.")
    async def yardim_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 Trendyol Takip Botu - Yardım (Slash Komutları)",
            description=f"Aşağıda kullanabileceğiniz slash komutlarının (`/`) listesi bulunmaktadır.\n"
                        f"Ayrıca prefix komutları (`{self.bot.command_prefix}`) da mevcuttur. Onlar için `{self.bot.command_prefix}yardım` kullanın.",
            color=discord.Color.purple()
        )
        # Slash komutlarını dinamik olarak listelemek için bot.tree.get_commands() kullanılabilir
        # Ancak bu basit bir statik liste olacak:
        embed.add_field(name="`/ekle [url]`", value="Takip edilecek Trendyol ürününü ekler.", inline=False)
        embed.add_field(name="`/takiptekiler`", value="Bu sunucuda takip edilen ürünleri listeler.", inline=False)
        embed.add_field(name="`/bilgi [urun_kimligi]`", value="Belirtilen ürün hakkında detaylı bilgi verir.", inline=False)
        embed.add_field(name="`/sil [urun_kimligi]`", value="Takip edilen bir ürünü listeden çıkarır.", inline=False)
        embed.add_field(name="`/guncelle [urun_kimligi]`", value="Ürün bilgilerini manuel olarak günceller.", inline=False)
        embed.add_field(name="`/yardim`", value="Bu yardım mesajını gösterir.", inline=False)
        
        embed.set_footer(text=f"Trendyol Takip Botu • Fiyat kontrol aralığı: {int(os.getenv('CHECK_INTERVAL', 3600))//60} dakika")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ProductCommands(bot))
