"""
Analitik ve istatistik komutları
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
from price_analyzer import PriceAnalyzer

logger = logging.getLogger(__name__)

class AnalyticsCommands(commands.Cog):
    def __init__(self, bot, database):
        self.bot = bot
        self.db = database
        self.analyzer = PriceAnalyzer(database)
    
    @app_commands.command(name="trend", description="Ürünün fiyat trendini gösterir")
    @app_commands.describe(product_id="Ürün ID'si veya URL")
    async def trend_command(self, interaction: discord.Interaction, product_id: str):
        """Ürün fiyat trendini gösterir"""
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
                await interaction.followup.send("❌ Bu ürün takip listesinde bulunamadı!")
                return
            
            # Trend analizi yap
            trend_data = self.analyzer.get_price_trend(product_id, days=30)
            
            if not trend_data or trend_data['trend'] == 'insufficient_data':
                await interaction.followup.send("📊 Bu ürün için yeterli fiyat verisi bulunmuyor.")
                return
            
            # Embed oluştur
            embed = discord.Embed(
                title=f"📈 Fiyat Trendi: {product['name'][:50]}...",
                color=self._get_trend_color(trend_data['trend']),
                url=product['url']
            )
            
            # Trend ikonu ve açıklama
            trend_icons = {
                'up': '📈 Yükseliş',
                'down': '📉 Düşüş', 
                'stable': '➡️ Stabil'
            }
            
            embed.add_field(
                name="Trend (30 gün)",
                value=f"{trend_icons.get(trend_data['trend'], '❓')} ({trend_data['change_percentage']:+.1f}%)",
                inline=True
            )
            
            embed.add_field(
                name="Mevcut Fiyat",
                value=f"₺{trend_data['last_price']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="Ortalama Fiyat",
                value=f"₺{trend_data['average_price']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="En Düşük",
                value=f"₺{trend_data['min_price']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="En Yüksek", 
                value=f"₺{trend_data['max_price']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="Veri Noktası",
                value=f"{trend_data['price_points']} kayıt",
                inline=True
            )
            
            # Fiyat geçmişi (son 5 kayıt)
            if trend_data['price_history']:
                history_text = ""
                for date, price in trend_data['price_history'][-5:]:
                    date_str = date[:10]  # YYYY-MM-DD formatı
                    history_text += f"`{date_str}` ₺{price:.2f}\n"
                
                embed.add_field(
                    name="Son Fiyat Değişiklikleri",
                    value=history_text,
                    inline=False
                )
            
            if product.get('image_url'):
                embed.set_thumbnail(url=product['image_url'])
            
            embed.set_footer(text=f"Ürün ID: {product_id}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Trend komutu hatası: {e}")
            await interaction.followup.send("❌ Trend analizi sırasında bir hata oluştu!")
    
    @app_commands.command(name="deals", description="En iyi fırsatları gösterir")
    async def deals_command(self, interaction: discord.Interaction):
        """En iyi fırsatları listeler"""
        await interaction.response.defer()
        
        try:
            deals = self.analyzer.get_best_deals(guild_id=str(interaction.guild_id), limit=10)
            
            if not deals:
                await interaction.followup.send("🛍️ Şu anda aktif fırsat bulunmuyor.")
                return
            
            embed = discord.Embed(
                title="🔥 En İyi Fırsatlar (Son 7 Gün)",
                description="Fiyatı en çok düşen ürünler",
                color=discord.Color.green()
            )
            
            for i, deal in enumerate(deals[:5], 1):
                embed.add_field(
                    name=f"{i}. {deal['name'][:40]}...",
                    value=f"~~₺{deal['old_price']:.2f}~~ → **₺{deal['current_price']:.2f}**\n"
                          f"💰 **%{deal['discount_percentage']:.1f}** indirim (₺{deal['savings']:.2f} tasarruf)",
                    inline=False
                )
            
            if len(deals) > 5:
                embed.set_footer(text=f"Toplam {len(deals)} fırsat bulundu. İlk 5'i gösteriliyor.")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Fırsatlar komutu hatası: {e}")
            await interaction.followup.send("❌ Fırsatlar analizi sırasında bir hata oluştu!")
    
    @app_commands.command(name="alerts", description="Fiyat uyarılarını gösterir")
    @app_commands.describe(threshold="Uyarı eşiği (varsayılan: %10)")
    async def alerts_command(self, interaction: discord.Interaction, threshold: int = 10):
        """Fiyat uyarılarını gösterir"""
        await interaction.response.defer()
        
        try:
            alerts = self.analyzer.get_price_alerts(
                guild_id=str(interaction.guild_id), 
                threshold=threshold
            )
            
            if not alerts:
                await interaction.followup.send(f"🔔 %{threshold} eşiğini aşan fiyat değişikliği bulunmuyor.")
                return
            
            embed = discord.Embed(
                title=f"🚨 Fiyat Uyarıları (%{threshold}+ değişim)",
                color=discord.Color.orange()
            )
            
            increases = [a for a in alerts if a['alert_type'] == 'increase']
            decreases = [a for a in alerts if a['alert_type'] == 'decrease']
            
            if increases:
                increase_text = ""
                for alert in increases[:3]:
                    increase_text += f"**{alert['name'][:30]}...**\n"
                    increase_text += f"₺{alert['previous_price']:.2f} → ₺{alert['current_price']:.2f} "
                    increase_text += f"(+%{alert['change_percentage']:.1f})\n\n"
                
                embed.add_field(
                    name="📈 Fiyat Artışları",
                    value=increase_text,
                    inline=False
                )
            
            if decreases:
                decrease_text = ""
                for alert in decreases[:3]:
                    decrease_text += f"**{alert['name'][:30]}...**\n"
                    decrease_text += f"₺{alert['previous_price']:.2f} → ₺{alert['current_price']:.2f} "
                    decrease_text += f"(%{alert['change_percentage']:.1f})\n\n"
                
                embed.add_field(
                    name="📉 Fiyat Düşüşleri",
                    value=decrease_text,
                    inline=False
                )
            
            total_alerts = len(increases) + len(decreases)
            if total_alerts > 6:
                embed.set_footer(text=f"Toplam {total_alerts} uyarı bulundu. İlk 6'sı gösteriliyor.")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Uyarılar komutu hatası: {e}")
            await interaction.followup.send("❌ Uyarılar analizi sırasında bir hata oluştu!")
    
    @app_commands.command(name="stats", description="Sunucu istatistiklerini gösterir")
    async def stats_command(self, interaction: discord.Interaction):
        """Sunucu istatistiklerini gösterir"""
        await interaction.response.defer()
        
        try:
            stats = self.analyzer.get_guild_statistics(str(interaction.guild_id))
            
            if not stats or stats['total_products'] == 0:
                await interaction.followup.send("📊 Bu sunucuda henüz takip edilen ürün bulunmuyor.")
                return
            
            embed = discord.Embed(
                title=f"📊 {interaction.guild.name} İstatistikleri",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📦 Toplam Ürün",
                value=f"{stats['total_products']} ürün",
                inline=True
            )
            
            embed.add_field(
                name="💰 Ortalama Fiyat",
                value=f"₺{stats['average_price']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="🆕 Bugün Eklenen",
                value=f"{stats['products_added_today']} ürün",
                inline=True
            )
            
            embed.add_field(
                name="💎 En Pahalı",
                value=f"{stats['most_expensive']['name'][:30]}...\n₺{stats['most_expensive']['price']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="💸 En Ucuz",
                value=f"{stats['cheapest']['name'][:30]}...\n₺{stats['cheapest']['price']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="📈 Toplam Değer",
                value=f"₺{stats['average_price'] * stats['total_products']:.2f}",
                inline=True
            )
            
            embed.set_footer(text="Son güncelleme: Şimdi")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"İstatistikler komutu hatası: {e}")
            await interaction.followup.send("❌ İstatistikler analizi sırasında bir hata oluştu!")
    
    def _get_trend_color(self, trend):
        """Trend durumuna göre renk döndürür"""
        colors = {
            'up': discord.Color.red(),
            'down': discord.Color.green(),
            'stable': discord.Color.blue()
        }
        return colors.get(trend, discord.Color.grey())

async def setup(bot):
    """Cog'u bot'a ekler"""
    pass  # Bu fonksiyon main.py'da manuel olarak çağrılacak