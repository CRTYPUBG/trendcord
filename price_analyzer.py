"""
Fiyat analizi ve trend hesaplama modülü
"""
import sqlite3
from datetime import datetime, timedelta
import statistics
import logging

logger = logging.getLogger(__name__)

class PriceAnalyzer:
    def __init__(self, database):
        self.db = database
    
    def get_price_trend(self, product_id, days=30):
        """
        Ürünün fiyat trendini analiz eder
        
        Returns:
            dict: {
                'trend': 'up'|'down'|'stable',
                'change_percentage': float,
                'average_price': float,
                'min_price': float,
                'max_price': float,
                'price_points': list
            }
        """
        try:
            # Son N günün fiyat verilerini al
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            self.db.cursor.execute('''
                SELECT price, date FROM price_history 
                WHERE product_id = ? AND date >= ?
                ORDER BY date ASC
            ''', (product_id, cutoff_date))
            
            results = self.db.cursor.fetchall()
            
            if len(results) < 2:
                return {
                    'trend': 'insufficient_data',
                    'change_percentage': 0,
                    'average_price': results[0][0] if results else 0,
                    'min_price': results[0][0] if results else 0,
                    'max_price': results[0][0] if results else 0,
                    'price_points': len(results)
                }
            
            prices = [row[0] for row in results]
            dates = [row[1] for row in results]
            
            # Temel istatistikler
            first_price = prices[0]
            last_price = prices[-1]
            avg_price = statistics.mean(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            # Trend hesaplama
            change_percentage = ((last_price - first_price) / first_price) * 100
            
            if change_percentage > 5:
                trend = 'up'
            elif change_percentage < -5:
                trend = 'down'
            else:
                trend = 'stable'
            
            return {
                'trend': trend,
                'change_percentage': round(change_percentage, 2),
                'average_price': round(avg_price, 2),
                'min_price': min_price,
                'max_price': max_price,
                'price_points': len(prices),
                'first_price': first_price,
                'last_price': last_price,
                'price_history': list(zip(dates, prices))
            }
            
        except Exception as e:
            logger.error(f"Fiyat trend analizi hatası: {e}")
            return None
    
    def get_best_deals(self, guild_id=None, limit=10):
        """En iyi fırsatları (en çok düşen fiyatlar) bulur"""
        try:
            # Son 7 günde en çok düşen ürünleri bul
            query = '''
                SELECT p.product_id, p.name, p.current_price, p.url,
                       (SELECT price FROM price_history ph1 
                        WHERE ph1.product_id = p.product_id 
                        AND ph1.date >= date('now', '-7 days')
                        ORDER BY ph1.date ASC LIMIT 1) as week_ago_price
                FROM products p
                WHERE p.current_price IS NOT NULL
            '''
            
            params = []
            if guild_id:
                query += ' AND p.guild_id = ?'
                params.append(guild_id)
            
            self.db.cursor.execute(query, params)
            results = self.db.cursor.fetchall()
            
            deals = []
            for row in results:
                if row[4] and row[2] < row[4]:  # week_ago_price exists and current < week_ago
                    discount = ((row[4] - row[2]) / row[4]) * 100
                    deals.append({
                        'product_id': row[0],
                        'name': row[1],
                        'current_price': row[2],
                        'url': row[3],
                        'old_price': row[4],
                        'discount_percentage': round(discount, 2),
                        'savings': round(row[4] - row[2], 2)
                    })
            
            # İndirim oranına göre sırala
            deals.sort(key=lambda x: x['discount_percentage'], reverse=True)
            return deals[:limit]
            
        except Exception as e:
            logger.error(f"En iyi fırsatlar analizi hatası: {e}")
            return []
    
    def get_price_alerts(self, guild_id=None, threshold=10):
        """Belirli eşiği aşan fiyat değişikliklerini bulur"""
        try:
            query = '''
                SELECT p.product_id, p.name, p.current_price, p.url,
                       ph.price as previous_price, ph.date as previous_date
                FROM products p
                JOIN (
                    SELECT product_id, price, date,
                           ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY date DESC) as rn
                    FROM price_history
                ) ph ON p.product_id = ph.product_id AND ph.rn = 2
                WHERE p.current_price IS NOT NULL
            '''
            
            params = []
            if guild_id:
                query += ' AND p.guild_id = ?'
                params.append(guild_id)
            
            self.db.cursor.execute(query, params)
            results = self.db.cursor.fetchall()
            
            alerts = []
            for row in results:
                if row[4]:  # previous_price exists
                    change_percentage = ((row[2] - row[4]) / row[4]) * 100
                    
                    if abs(change_percentage) >= threshold:
                        alerts.append({
                            'product_id': row[0],
                            'name': row[1],
                            'current_price': row[2],
                            'url': row[3],
                            'previous_price': row[4],
                            'change_percentage': round(change_percentage, 2),
                            'change_amount': round(row[2] - row[4], 2),
                            'alert_type': 'increase' if change_percentage > 0 else 'decrease'
                        })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Fiyat uyarıları analizi hatası: {e}")
            return []
    
    def get_guild_statistics(self, guild_id):
        """Sunucu istatistiklerini hesaplar"""
        try:
            stats = {}
            
            # Toplam ürün sayısı
            self.db.cursor.execute('''
                SELECT COUNT(*) FROM products WHERE guild_id = ?
            ''', (guild_id,))
            stats['total_products'] = self.db.cursor.fetchone()[0]
            
            # Ortalama fiyat
            self.db.cursor.execute('''
                SELECT AVG(current_price) FROM products 
                WHERE guild_id = ? AND current_price IS NOT NULL
            ''', (guild_id,))
            avg_result = self.db.cursor.fetchone()[0]
            stats['average_price'] = round(avg_result, 2) if avg_result else 0
            
            # En pahalı ve en ucuz ürün
            self.db.cursor.execute('''
                SELECT name, current_price FROM products 
                WHERE guild_id = ? AND current_price IS NOT NULL
                ORDER BY current_price DESC LIMIT 1
            ''', (guild_id,))
            most_expensive = self.db.cursor.fetchone()
            stats['most_expensive'] = {
                'name': most_expensive[0] if most_expensive else 'N/A',
                'price': most_expensive[1] if most_expensive else 0
            }
            
            self.db.cursor.execute('''
                SELECT name, current_price FROM products 
                WHERE guild_id = ? AND current_price IS NOT NULL
                ORDER BY current_price ASC LIMIT 1
            ''', (guild_id,))
            cheapest = self.db.cursor.fetchone()
            stats['cheapest'] = {
                'name': cheapest[0] if cheapest else 'N/A',
                'price': cheapest[1] if cheapest else 0
            }
            
            # Son 24 saatte eklenen ürün sayısı
            self.db.cursor.execute('''
                SELECT COUNT(*) FROM products 
                WHERE guild_id = ? AND added_at >= datetime('now', '-1 day')
            ''', (guild_id,))
            stats['products_added_today'] = self.db.cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Sunucu istatistikleri hatası: {e}")
            return {}