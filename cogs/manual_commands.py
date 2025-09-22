# cogs/manual_commands.py

import discord
from discord.ext import commands
from discord import app_commands
import re
import logging
from admin_utils import admin_manager

logger = logging.getLogger(__name__)

class ManualCommands(commands.Cog, name="Manuel Komutlar"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

    def _parse_price(self, price_text):
        """Fiyat metnini sayıya çevirir."""
        try:
            if not price_text:
                return None
            
            # TL, ₺ gibi para birimlerini kaldır
            price_text = re.sub(r'(TL|₺|tl)', '', str(price_text), flags=re.IGNORECASE).strip()
            
            # Sadece sayıları, virgül ve noktaları bırak
            price_clean = re.sub(r'[^\d,.]', '', price_text)
            
            if not price_clean:
                return None
            
            # Türkçe format handling
            if ',' in price_clean:
                parts = price_clean.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Ondalık ayırıcı: 123,45
                    price_clean = price_clean.replace(',', '.')
                else:
                    # Binlik ayırıcı: 1,234
                    price_clean = price_clean.replace(',', '')
            
            result = float(price_clean)
            
            if 0.01 <= result <= 1000000:
                return result
            else:
                return None
            
        except (ValueError, AttributeError):
            return None

    def _extract_product_id_from_url(self, url):
        """URL'den ürün ID'sini çıkarır."""
        try:
            patterns = [
                r'/[^/]+-p-(\d+)',  # Standard format
                r'productId[=:](\d+)',
                r'pi[=:](\d+)',
                r'/p/(\d+)',
                r'p-(\d+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
                    
            return None
        except:
            return None

    @commands.command(name="manuel_ekle", help="Ürünü manuel olarak takip listesine ekler. Kullanım: !manuel_ekle \"Ürün Adı\" fiyat URL")
    @commands.guild_only()
    async def manuel_ekle_prefix(self, ctx: commands.Context, name: str = None, price: str = None, url: str = None):
        """Manuel ürün ekleme komutu"""
        if not all([name, price, url]):
            await ctx.send(
                f"❌ Eksik parametre! Doğru kullanım:\n"
                f"`{self.bot.command_prefix}manuel_ekle \"Ürün Adı\" 299.99 \"https://www.trendyol.com/...\"`\n\n"
                f"Örnek:\n"
                f"`{self.bot.command_prefix}manuel_ekle \"iPhone 15\" 45999.99 \"https://www.trendyol.com/apple/iphone-15-p-123456\"`"
            )
            return

        try:
            # Fiyatı parse et
            parsed_price = self._parse_price(price)
            if parsed_price is None:
                await ctx.send(f"❌ Geçersiz fiyat formatı: `{price}`. Örnek: 299.99 veya 1.299,50")
                return

            # URL'den ürün ID'si çıkar
            product_id = self._extract_product_id_from_url(url)
            if not product_id:
                # Eğer URL'den ID çıkaramazsa, URL'nin hash'ini kullan
                import hashlib
                product_id = "manual_" + hashlib.md5(url.encode()).hexdigest()[:8]

            # URL doğrulama
            if not ("trendyol.com" in url.lower() or url.startswith("http")):
                await ctx.send("❌ Geçerli bir URL girin. URL 'trendyol.com' içermeli veya 'http' ile başlamalı.")
                return

            # Manuel ürün verisi oluştur
            product_data = {
                'product_id': product_id,
                'name': name,
                'url': url,
                'image_url': None,
                'current_price': parsed_price,
                'original_price': parsed_price,
                'success': True
            }

            # Veritabanına ekle
            if self.db.add_product(product_data, str(ctx.guild.id), str(ctx.author.id), str(ctx.channel.id)):
                embed = discord.Embed(
                    title="✅ Ürün Manuel Olarak Eklendi",
                    description=f"**{name}** takip listesine manuel olarak eklendi!",
                    color=discord.Color.green()
                )
                embed.add_field(name="Ürün ID", value=product_id, inline=True)
                embed.add_field(name="Fiyat", value=f"{parsed_price:.2f} TL", inline=True)
                embed.add_field(name="URL", value=f"[Trendyol'da Görüntüle]({url})", inline=False)
                embed.set_footer(text=f"Ekleyen: {ctx.author.name} • Manuel eklenen ürünlerin fiyatları otomatik güncellenmeyebilir.")
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Ürün eklenirken bir hata oluştu veya bu ürün zaten mevcut.")

        except Exception as e:
            logger.error(f"Manuel ürün ekleme hatası: {e}")
            await ctx.send(f"❌ Ürün eklenirken bir hata oluştu: {str(e)}")

    @commands.command(name="fiyat_guncelle", help="Manuel eklenen ürünün fiyatını günceller. Kullanım: !fiyat_guncelle ID yeni_fiyat")
    @commands.guild_only()
    async def fiyat_guncelle_prefix(self, ctx: commands.Context, product_id: str = None, new_price: str = None):
        """Manuel fiyat güncelleme komutu"""
        if not all([product_id, new_price]):
            await ctx.send(
                f"❌ Eksik parametre! Doğru kullanım:\n"
                f"`{self.bot.command_prefix}fiyat_guncelle ÜRÜN_ID 399.99`"
            )
            return

        try:
            # Fiyatı parse et
            parsed_price = self._parse_price(new_price)
            if parsed_price is None:
                await ctx.send(f"❌ Geçersiz fiyat formatı: `{new_price}`. Örnek: 299.99 veya 1.299,50")
                return

            # Ürünün var olup olmadığını kontrol et
            product = self.db.get_product(product_id)
            if not product:
                await ctx.send(f"❌ ID'si `{product_id}` olan ürün bulunamadı.")
                return

            # Ürünün bu sunucuya ait olup olmadığını kontrol et
            if str(product.get('guild_id')) != str(ctx.guild.id):
                await ctx.send("❌ Bu ürün bu sunucuda takip edilmiyor.")
                return

            # Yetki kontrolü (sadece ürünü ekleyen, guild admin veya global admin)
            is_guild_admin = ctx.author.guild_permissions.administrator
            is_global_admin = admin_manager.is_global_admin(ctx.author.id)
            is_owner = str(product.get('user_id')) == str(ctx.author.id)
            
            if not (is_owner or is_guild_admin or is_global_admin):
                await ctx.send("❌ Bu ürünün fiyatını güncellemek için yetkiniz yok. Sadece ürünü ekleyen kişi, sunucu adminleri veya global adminler güncelleyebilir.")
                return

            # Fiyatı güncelle
            old_price = product.get('current_price')
            if self.db.update_product_price(product_id, parsed_price):
                embed = discord.Embed(
                    title="✅ Fiyat Manuel Olarak Güncellendi",
                    description=f"**{product.get('name', 'İsimsiz Ürün')}** fiyatı güncellendi.",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Eski Fiyat", value=f"{old_price:.2f} TL" if old_price else "Bilinmiyor", inline=True)
                embed.add_field(name="Yeni Fiyat", value=f"{parsed_price:.2f} TL", inline=True)
                
                if old_price and old_price != parsed_price:
                    price_diff = parsed_price - old_price
                    percentage = abs(price_diff / old_price * 100) if old_price != 0 else 0
                    change_direction = "düşüş" if price_diff < 0 else "artış"
                    emoji = "🔽" if price_diff < 0 else "🔼"
                    embed.add_field(name="Değişim", value=f"{emoji} {abs(price_diff):.2f} TL {change_direction} (%{percentage:.1f})", inline=False)
                    embed.color = discord.Color.green() if price_diff < 0 else discord.Color.red()
                
                embed.set_footer(text=f"Güncelleyen: {ctx.author.name}")
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Fiyat güncellenirken bir hata oluştu.")

        except Exception as e:
            logger.error(f"Manuel fiyat güncelleme hatası: {e}")
            await ctx.send(f"❌ Fiyat güncellenirken bir hata oluştu: {str(e)}")

    @app_commands.command(name="manuel_ekle", description="Ürünü manuel olarak takip listesine ekler.")
    @app_commands.describe(
        name="Ürün adı",
        price="Ürün fiyatı (örn: 299.99)",
        url="Ürün URL'si"
    )
    @app_commands.guild_only()
    async def manuel_ekle_slash(self, interaction: discord.Interaction, name: str, price: str, url: str):
        """Manuel ürün ekleme slash komutu"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Fiyatı parse et
            parsed_price = self._parse_price(price)
            if parsed_price is None:
                await interaction.followup.send(f"❌ Geçersiz fiyat formatı: `{price}`. Örnek: 299.99 veya 1.299,50")
                return

            # URL'den ürün ID'si çıkar
            product_id = self._extract_product_id_from_url(url)
            if not product_id:
                import hashlib
                product_id = "manual_" + hashlib.md5(url.encode()).hexdigest()[:8]

            # URL doğrulama
            if not ("trendyol.com" in url.lower() or url.startswith("http")):
                await interaction.followup.send("❌ Geçerli bir URL girin. URL 'trendyol.com' içermeli veya 'http' ile başlamalı.")
                return

            # Manuel ürün verisi oluştur
            product_data = {
                'product_id': product_id,
                'name': name,
                'url': url,
                'image_url': None,
                'current_price': parsed_price,
                'original_price': parsed_price,
                'success': True
            }

            # Veritabanına ekle
            if self.db.add_product(product_data, str(interaction.guild.id), str(interaction.user.id), str(interaction.channel.id)):
                embed = discord.Embed(
                    title="✅ Ürün Manuel Olarak Eklendi (Slash)",
                    description=f"**{name}** takip listesine manuel olarak eklendi!",
                    color=discord.Color.purple()
                )
                embed.add_field(name="Ürün ID", value=product_id, inline=True)
                embed.add_field(name="Fiyat", value=f"{parsed_price:.2f} TL", inline=True)
                embed.add_field(name="URL", value=f"[Trendyol'da Görüntüle]({url})", inline=False)
                embed.set_footer(text=f"Ekleyen: {interaction.user.name} • Manuel eklenen ürünlerin fiyatları otomatik güncellenmeyebilir.")
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Ürün eklenirken bir hata oluştu veya bu ürün zaten mevcut.")

        except Exception as e:
            logger.error(f"Manuel ürün ekleme hatası: {e}")
            await interaction.followup.send(f"❌ Ürün eklenirken bir hata oluştu: {str(e)}")

    @app_commands.command(name="fiyat_guncelle", description="Manuel eklenen ürünün fiyatını günceller.")
    @app_commands.describe(
        product_id="Ürün ID'si",
        new_price="Yeni fiyat (örn: 399.99)"
    )
    @app_commands.guild_only()
    async def fiyat_guncelle_slash(self, interaction: discord.Interaction, product_id: str, new_price: str):
        """Manuel fiyat güncelleme slash komutu"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Fiyatı parse et
            parsed_price = self._parse_price(new_price)
            if parsed_price is None:
                await interaction.followup.send(f"❌ Geçersiz fiyat formatı: `{new_price}`. Örnek: 299.99 veya 1.299,50")
                return

            # Ürünün var olup olmadığını kontrol et
            product = self.db.get_product(product_id)
            if not product:
                await interaction.followup.send(f"❌ ID'si `{product_id}` olan ürün bulunamadı.")
                return

            # Ürünün bu sunucuya ait olup olmadığını kontrol et
            if str(product.get('guild_id')) != str(interaction.guild.id):
                await interaction.followup.send("❌ Bu ürün bu sunucuda takip edilmiyor.")
                return

            # Yetki kontrolü
            is_guild_admin = interaction.user.guild_permissions.administrator
            is_global_admin = admin_manager.is_global_admin(interaction.user.id)
            is_owner = str(product.get('user_id')) == str(interaction.user.id)
            
            if not (is_owner or is_guild_admin or is_global_admin):
                await interaction.followup.send("❌ Bu ürünün fiyatını güncellemek için yetkiniz yok. Sadece ürünü ekleyen kişi, sunucu adminleri veya global adminler güncelleyebilir.")
                return

            # Fiyatı güncelle
            old_price = product.get('current_price')
            if self.db.update_product_price(product_id, parsed_price):
                embed = discord.Embed(
                    title="✅ Fiyat Manuel Olarak Güncellendi (Slash)",
                    description=f"**{product.get('name', 'İsimsiz Ürün')}** fiyatı güncellendi.",
                    color=discord.Color.purple()
                )
                embed.add_field(name="Eski Fiyat", value=f"{old_price:.2f} TL" if old_price else "Bilinmiyor", inline=True)
                embed.add_field(name="Yeni Fiyat", value=f"{parsed_price:.2f} TL", inline=True)
                
                if old_price and old_price != parsed_price:
                    price_diff = parsed_price - old_price
                    percentage = abs(price_diff / old_price * 100) if old_price != 0 else 0
                    change_direction = "düşüş" if price_diff < 0 else "artış"
                    emoji = "🔽" if price_diff < 0 else "🔼"
                    embed.add_field(name="Değişim", value=f"{emoji} {abs(price_diff):.2f} TL {change_direction} (%{percentage:.1f})", inline=False)
                    embed.color = discord.Color.green() if price_diff < 0 else discord.Color.red()
                
                embed.set_footer(text=f"Güncelleyen: {interaction.user.name}")
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Fiyat güncellenirken bir hata oluştu.")

        except Exception as e:
            logger.error(f"Manuel fiyat güncelleme hatası: {e}")
            await interaction.followup.send(f"❌ Fiyat güncellenirken bir hata oluştu: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ManualCommands(bot))