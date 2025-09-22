"""
Bildirim sistemi komutları
Fiyat hedefleri, uyarılar ve bildirim yönetimi
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
from notification_system import NotificationSystem

logger = logging.getLogger(__name__)

class NotificationCommands(commands.Cog):
    def __init__(self, bot, database):
        self.bot = bot
        self.db = database
        self.notification_system = NotificationSystem(database)
    
    @app_commands.command(name="hedef", description="Ürün için fiyat hedefi belirle")
    @app_commands.describe(
        product_id="Ürün ID'si veya URL",
        target_price="Hedef fiyat (TL)",
        condition="Koşul: below (altında), above (üstünde)"
    )
    @app_commands.choices(condition=[
        app_commands.Choice(name="Altında (fiyat düştüğünde)", value="below"),
        app_commands.Choice(name="Üstünde (fiyat çıktığında)", value="above")
    ])
    async def set_price_target(self, interaction: discord.Interaction, product_id: str, target_price: float, condition: str = "below"):
        """Ürün için fiyat hedefi belirle"""
        await interaction.response.defer()
        
        try:
            # URL'den product_id çıkar
            if 'trendyol.com' in product_id or 'ty.gl' in product_id:
                from scraper import TrendyolScraper
                scraper = TrendyolScraper()
                extracted_id = scraper.extract_product_id(product_id)
                if extracted_id:
                    product_id = extracted_id
                else:
                    await interaction.followup.send("❌ Geçersiz ürün URL'si!")
                    return
            
            # Ürünün varlığını kontrol et
            product = self.db.get_product(product_id)
            if not product:
                await interaction.followup.send("❌ Bu ürün takip listesinde bulunamadı! Önce ürünü ekleyin.")
                return
            
            # Fiyat hedefi ekle
            success = self.notification_system.add_price_target(
                product_id=product_id,
                user_id=str(interaction.user.id),
                guild_id=str(interaction.guild_id),
                channel_id=str(interaction.channel_id),
                target_price=target_price,
                condition=condition
            )
            
            if success:
                condition_text = {
                    'below': f'₺{target_price:.2f} altına düştüğünde',
                    'above': f'₺{target_price:.2f} üstüne çıktığında'
                }
                
                embed = discord.Embed(
                    title="🎯 Fiyat Hedefi Belirlendi",
                    description=f"**{product['name'][:50]}...**",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="Hedef",
                    value=condition_text.get(condition, f"₺{target_price:.2f}"),
                    inline=True
                )
                
                embed.add_field(
                    name="Mevcut Fiyat",
                    value=f"₺{product['current_price']:.2f}",
                    inline=True
                )
                
                embed.add_field(
                    name="Durum",
                    value="🟢 Aktif",
                    inline=True
                )
                
                if product.get('image_url'):
                    embed.set_thumbnail(url=product['image_url'])
                
                embed.set_footer(text="Hedef gerçekleştiğinde bildirim alacaksınız!")
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Fiyat hedefi belirlenirken bir hata oluştu!")
                
        except Exception as e:
            logger.error(f"Fiyat hedefi komutu hatası: {e}")
            await interaction.followup.send("❌ Fiyat hedefi belirlenirken bir hata oluştu!")
    
    @app_commands.command(name="hedeflerim", description="Aktif fiyat hedeflerimi göster")
    async def my_price_targets(self, interaction: discord.Interaction):
        """Kullanıcının aktif fiyat hedeflerini göster"""
        await interaction.response.defer()
        
        try:
            targets = self.notification_system.get_user_price_targets(
                user_id=str(interaction.user.id),
                guild_id=str(interaction.guild_id)
            )
            
            if not targets:
                await interaction.followup.send("🎯 Henüz aktif fiyat hedefiniz bulunmuyor.\n`/hedef` komutu ile fiyat hedefi belirleyebilirsiniz.")
                return
            
            embed = discord.Embed(
                title=f"🎯 {interaction.user.display_name} - Aktif Fiyat Hedefleri",
                color=discord.Color.blue()
            )
            
            for i, target in enumerate(targets[:10], 1):  # İlk 10 hedef
                condition_emoji = "📉" if target['condition'] == 'below' else "📈"
                condition_text = "altına düşerse" if target['condition'] == 'below' else "üstüne çıkarsa"
                
                # Hedefe ne kadar kaldığını hesapla
                current_price = target['current_price']
                target_price = target['target_price']
                
                if target['condition'] == 'below':
                    distance = current_price - target_price
                    distance_text = f"₺{distance:.2f} daha düşmeli" if distance > 0 else "🎉 Hedef gerçekleşti!"
                else:
                    distance = target_price - current_price
                    distance_text = f"₺{distance:.2f} daha yükselmeli" if distance > 0 else "🎉 Hedef gerçekleşti!"
                
                embed.add_field(
                    name=f"{condition_emoji} {target['product_name'][:30]}...",
                    value=f"**Hedef:** ₺{target_price:.2f} {condition_text}\n"
                          f"**Mevcut:** ₺{current_price:.2f}\n"
                          f"**Durum:** {distance_text}",
                    inline=False
                )
            
            if len(targets) > 10:
                embed.set_footer(text=f"Toplam {len(targets)} hedef var. İlk 10'u gösteriliyor.")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Fiyat hedefleri listesi hatası: {e}")
            await interaction.followup.send("❌ Fiyat hedefleri getirilirken bir hata oluştu!")
    
    @app_commands.command(name="hedef-sil", description="Fiyat hedefini kaldır")
    @app_commands.describe(target_id="Hedef ID'si (hedeflerim komutundan)")
    async def remove_price_target(self, interaction: discord.Interaction, target_id: int):
        """Fiyat hedefini kaldır"""
        await interaction.response.defer()
        
        try:
            success = self.notification_system.remove_price_target(
                target_id=target_id,
                user_id=str(interaction.user.id)
            )
            
            if success:
                embed = discord.Embed(
                    title="🗑️ Fiyat Hedefi Kaldırıldı",
                    description="Fiyat hedefi başarıyla kaldırıldı.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Fiyat hedefi bulunamadı veya kaldırılamadı!")
                
        except Exception as e:
            logger.error(f"Fiyat hedefi silme hatası: {e}")
            await interaction.followup.send("❌ Fiyat hedefi kaldırılırken bir hata oluştu!")
    
    @app_commands.command(name="bildirimlerim", description="Bildirim geçmişimi göster")
    async def my_notifications(self, interaction: discord.Interaction):
        """Kullanıcının bildirim geçmişini göster"""
        await interaction.response.defer()
        
        try:
            notifications = self.notification_system.get_notification_history(
                user_id=str(interaction.user.id),
                guild_id=str(interaction.guild_id),
                limit=10
            )
            
            if not notifications:
                await interaction.followup.send("📬 Henüz bildirim geçmişiniz bulunmuyor.")
                return
            
            embed = discord.Embed(
                title=f"📬 {interaction.user.display_name} - Bildirim Geçmişi",
                color=discord.Color.purple()
            )
            
            for notification in notifications:
                # Bildirim türüne göre emoji
                type_emojis = {
                    'price_target': '🎯',
                    'price_drop': '📉',
                    'stock_alert': '📦',
                    'daily_summary': '📊'
                }
                
                emoji = type_emojis.get(notification['notification_type'], '📢')
                read_status = "✅" if notification['is_read'] else "🔴"
                
                # Tarih formatla
                sent_date = notification['sent_at'][:10]  # YYYY-MM-DD
                
                embed.add_field(
                    name=f"{emoji} {read_status} {notification['product_name'] or 'Genel'}",
                    value=f"{notification['message'][:100]}...\n*{sent_date}*",
                    inline=False
                )
            
            # Okunmamış bildirim sayısı
            unread_count = sum(1 for n in notifications if not n['is_read'])
            if unread_count > 0:
                embed.set_footer(text=f"{unread_count} okunmamış bildirim var")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Bildirim geçmişi hatası: {e}")
            await interaction.followup.send("❌ Bildirim geçmişi getirilirken bir hata oluştu!")
    
    @app_commands.command(name="ozet", description="Günlük fiyat özeti")
    async def daily_summary(self, interaction: discord.Interaction):
        """Günlük fiyat özeti göster"""
        await interaction.response.defer()
        
        try:
            summary = self.notification_system.get_daily_summary(str(interaction.guild_id))
            
            if not summary:
                await interaction.followup.send("📊 Günlük özet verisi bulunamadı.")
                return
            
            embed = discord.Embed(
                title="📊 Günlük Fiyat Özeti",
                description=f"**{summary['date']}** tarihli özet",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🆕 Bugün Eklenen Ürünler",
                value=f"{summary['products_added_today']} ürün",
                inline=True
            )
            
            embed.add_field(
                name="📈 Dün Fiyat Değişen Ürünler",
                value=f"{summary['price_changes_yesterday']} ürün",
                inline=True
            )
            
            embed.add_field(
                name="🔥 En İyi Fırsatlar",
                value=f"{len(summary['biggest_drops'])} fırsat",
                inline=True
            )
            
            # En çok düşen fiyatlar
            if summary['biggest_drops']:
                drops_text = ""
                for drop in summary['biggest_drops'][:3]:
                    drops_text += f"**{drop['name'][:25]}...**\n"
                    drops_text += f"₺{drop['yesterday_price']:.2f} → ₺{drop['current_price']:.2f} "
                    drops_text += f"(-%{drop['drop_percentage']:.1f})\n\n"
                
                embed.add_field(
                    name="📉 En Çok Düşen Fiyatlar",
                    value=drops_text,
                    inline=False
                )
            
            embed.set_footer(text="Günlük özetler otomatik olarak hesaplanır")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Günlük özet hatası: {e}")
            await interaction.followup.send("❌ Günlük özet getirilirken bir hata oluştu!")

async def setup(bot):
    """Cog'u bot'a ekler"""
    pass  # Bu fonksiyon main.py'da manuel olarak çağrılacak