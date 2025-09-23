"""
Site Monitoring Commands
Trendyol site monitoring sistemi için Discord komutları
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import logging
from site_monitor import site_monitor
from admin_utils import is_global_admin

logger = logging.getLogger(__name__)

class MonitoringCommands(commands.Cog):
    """Site monitoring komutları"""
    
    def __init__(self, bot):
        self.bot = bot
        self.monitoring_task.start()
    
    def cog_unload(self):
        """Cog kaldırılırken task'ı durdur"""
        self.monitoring_task.cancel()
    
    @tasks.loop(hours=48)  # 2 günde bir çalış
    async def monitoring_task(self):
        """2 günde bir site monitoring kontrolü"""
        try:
            logger.info("🔍 Otomatik site monitoring kontrolü başlıyor...")
            await site_monitor.run_monitoring_check(self.bot)
            logger.info("✅ Otomatik site monitoring kontrolü tamamlandı")
        except Exception as e:
            logger.error(f"Monitoring task hatası: {e}")
    
    @monitoring_task.before_loop
    async def before_monitoring_task(self):
        """Task başlamadan önce bot'un hazır olmasını bekle"""
        await self.bot.wait_until_ready()
        logger.info("🤖 Site monitoring task başlatıldı (2 günde bir çalışacak)")
    
    @commands.command(name='monitoring_check', aliases=['site_check', 'check_site'])
    async def manual_monitoring_check(self, ctx):
        """Manuel site monitoring kontrolü (sadece global adminler)"""
        if not is_global_admin(ctx.author.id):
            await ctx.send("❌ Bu komutu sadece global adminler kullanabilir.")
            return
        
        embed = discord.Embed(
            title="🔍 Site Monitoring Kontrolü",
            description="Manuel kontrol başlatılıyor...",
            color=0x3498db
        )
        message = await ctx.send(embed=embed)
        
        try:
            # Monitoring kontrolünü çalıştır
            await site_monitor.run_monitoring_check(self.bot)
            
            embed = discord.Embed(
                title="✅ Site Monitoring Tamamlandı",
                description="Kontrol tamamlandı. Sonuçlar DM olarak gönderildi.",
                color=0x2ecc71
            )
            embed.add_field(
                name="📊 Kontrol Detayları",
                value=f"🕐 Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                      f"🔍 Kontrol Türü: Manuel\n"
                      f"👤 Başlatan: {ctx.author.mention}",
                inline=False
            )
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Manuel monitoring hatası: {e}")
            
            embed = discord.Embed(
                title="❌ Site Monitoring Hatası",
                description=f"Kontrol sırasında hata oluştu: {str(e)}",
                color=0xe74c3c
            )
            await message.edit(embed=embed)
    
    @commands.command(name='monitoring_status', aliases=['monitor_status'])
    async def monitoring_status(self, ctx):
        """Monitoring sisteminin durumunu göster (sadece global adminler)"""
        if not is_global_admin(ctx.author.id):
            await ctx.send("❌ Bu komutu sadece global adminler kullanabilir.")
            return
        
        try:
            # Son kontrol bilgilerini al
            previous_structure = site_monitor.load_previous_structure()
            
            embed = discord.Embed(
                title="📊 Site Monitoring Durumu",
                color=0x3498db
            )
            
            if previous_structure:
                last_check = datetime.fromisoformat(previous_structure.last_check)
                next_check = last_check + timedelta(hours=48)
                
                embed.add_field(
                    name="🕐 Son Kontrol",
                    value=last_check.strftime('%d.%m.%Y %H:%M'),
                    inline=True
                )
                embed.add_field(
                    name="⏰ Sonraki Kontrol",
                    value=next_check.strftime('%d.%m.%Y %H:%M'),
                    inline=True
                )
                embed.add_field(
                    name="🔄 Durum",
                    value="✅ Aktif" if self.monitoring_task.is_running() else "❌ Pasif",
                    inline=True
                )
                
                embed.add_field(
                    name="📊 Site Yapısı",
                    value=f"JSON-LD: {'✅' if previous_structure.json_ld_present else '❌'}\n"
                          f"Fiyat Selektörleri: {len(previous_structure.price_selectors)}\n"
                          f"API Endpoint'leri: {len(previous_structure.api_endpoints)}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚠️ Durum",
                    value="Henüz kontrol yapılmamış. İlk kontrol için `!monitoring_check` komutunu kullanın.",
                    inline=False
                )
            
            # Task durumu
            if self.monitoring_task.is_running():
                embed.add_field(
                    name="🤖 Otomatik Kontrol",
                    value="✅ Aktif (2 günde bir)",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🤖 Otomatik Kontrol",
                    value="❌ Pasif",
                    inline=True
                )
            
            embed.set_footer(text="Site monitoring sistemi Trendyol'daki değişiklikleri takip eder")
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Monitoring status hatası: {e}")
            await ctx.send(f"❌ Durum bilgisi alınırken hata oluştu: {str(e)}")
    
    @commands.command(name='monitoring_restart', aliases=['restart_monitor'])
    async def restart_monitoring(self, ctx):
        """Monitoring task'ını yeniden başlat (sadece global adminler)"""
        if not is_global_admin(ctx.author.id):
            await ctx.send("❌ Bu komutu sadece global adminler kullanabilir.")
            return
        
        try:
            # Task'ı durdur ve yeniden başlat
            self.monitoring_task.cancel()
            await asyncio.sleep(1)
            self.monitoring_task.start()
            
            embed = discord.Embed(
                title="🔄 Monitoring Yeniden Başlatıldı",
                description="Site monitoring sistemi başarıyla yeniden başlatıldı.",
                color=0x2ecc71
            )
            embed.add_field(
                name="📊 Bilgi",
                value="Sistem 2 günde bir otomatik kontrol yapacak.",
                inline=False
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Monitoring restart hatası: {e}")
            await ctx.send(f"❌ Yeniden başlatma hatası: {str(e)}")
    
    @commands.command(name='monitoring_test', aliases=['test_monitor'])
    async def test_monitoring(self, ctx):
        """Monitoring sistemini test et (sadece global adminler)"""
        if not is_global_admin(ctx.author.id):
            await ctx.send("❌ Bu komutu sadece global adminler kullanabilir.")
            return
        
        embed = discord.Embed(
            title="🧪 Monitoring Test",
            description="Test başlatılıyor...",
            color=0xf39c12
        )
        message = await ctx.send(embed=embed)
        
        try:
            # Test URL'lerini kontrol et
            test_results = []
            
            for i, url in enumerate(site_monitor.test_urls, 1):
                embed.description = f"Test {i}/{len(site_monitor.test_urls)} - {url}"
                await message.edit(embed=embed)
                
                result = site_monitor.analyze_page_structure(url)
                
                if result.get('success'):
                    test_results.append(f"✅ Test {i}: Başarılı")
                else:
                    test_results.append(f"❌ Test {i}: Hata - {result.get('error', 'Bilinmeyen')}")
                
                await asyncio.sleep(2)  # Rate limiting
            
            # API endpoint testleri
            embed.description = "API endpoint'leri test ediliyor..."
            await message.edit(embed=embed)
            
            api_endpoints = site_monitor.check_api_endpoints()
            
            # Sonuçları göster
            embed = discord.Embed(
                title="🧪 Monitoring Test Sonuçları",
                color=0x2ecc71 if all("✅" in result for result in test_results) else 0xe74c3c
            )
            
            embed.add_field(
                name="🔍 Sayfa Testleri",
                value="\n".join(test_results),
                inline=False
            )
            
            embed.add_field(
                name="🌐 API Endpoint'leri",
                value=f"Aktif endpoint sayısı: {len(api_endpoints)}\n" + 
                      "\n".join([f"✅ {ep}" for ep in api_endpoints[:3]]) if api_endpoints else "❌ Aktif endpoint bulunamadı",
                inline=False
            )
            
            embed.set_footer(text=f"Test tamamlandı - {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Monitoring test hatası: {e}")
            
            embed = discord.Embed(
                title="❌ Test Hatası",
                description=f"Test sırasında hata oluştu: {str(e)}",
                color=0xe74c3c
            )
            await message.edit(embed=embed)

async def setup(bot):
    """Cog'u bot'a ekle"""
    await bot.add_cog(MonitoringCommands(bot))