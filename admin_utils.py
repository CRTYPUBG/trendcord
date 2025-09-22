import os
import logging
from typing import Union, List
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

logger = logging.getLogger(__name__)

class AdminManager:
    """Global admin yönetimi için yardımcı sınıf"""
    
    def __init__(self):
        self.global_admin_ids = self._load_global_admin_ids()
    
    def _load_global_admin_ids(self) -> List[int]:
        """Global admin ID'lerini .env dosyasından yükler"""
        try:
            admin_ids_str = os.getenv('GLOBAL_ADMIN_IDS', '')
            if not admin_ids_str:
                logger.warning("GLOBAL_ADMIN_IDS tanımlanmamış")
                return []
            
            # Virgülle ayrılmış ID'leri parse et
            admin_ids = []
            for id_str in admin_ids_str.split(','):
                id_str = id_str.strip()
                if id_str:
                    try:
                        admin_ids.append(int(id_str))
                    except ValueError:
                        logger.error(f"Geçersiz admin ID: {id_str}")
            
            logger.info(f"{len(admin_ids)} global admin yüklendi")
            return admin_ids
            
        except Exception as e:
            logger.error(f"Global admin ID'leri yüklenirken hata: {e}")
            return []
    
    def is_global_admin(self, user_id: Union[int, str]) -> bool:
        """Kullanıcının global admin olup olmadığını kontrol eder"""
        try:
            user_id = int(user_id)
            return user_id in self.global_admin_ids
        except (ValueError, TypeError):
            return False
    
    def is_admin(self, user, guild=None) -> bool:
        """
        Kullanıcının admin olup olmadığını kontrol eder
        Global admin veya sunucu admin'i olabilir
        """
        # Global admin kontrolü
        if self.is_global_admin(user.id):
            return True
        
        # Sunucu admin kontrolü
        if guild and hasattr(user, 'guild_permissions'):
            return user.guild_permissions.administrator
        
        return False
    
    def get_admin_level(self, user, guild=None) -> str:
        """Admin seviyesini döndürür"""
        if self.is_global_admin(user.id):
            return "global"
        elif guild and hasattr(user, 'guild_permissions') and user.guild_permissions.administrator:
            return "guild"
        else:
            return "none"
    
    def get_global_admin_list(self) -> List[int]:
        """Global admin listesini döndürür"""
        return self.global_admin_ids.copy()
    
    def add_global_admin(self, user_id: Union[int, str]) -> bool:
        """Global admin ekler (runtime'da, .env'e kaydetmez)"""
        try:
            user_id = int(user_id)
            if user_id not in self.global_admin_ids:
                self.global_admin_ids.append(user_id)
                logger.info(f"Global admin eklendi: {user_id}")
                return True
            return False
        except (ValueError, TypeError):
            return False
    
    def remove_global_admin(self, user_id: Union[int, str]) -> bool:
        """Global admin kaldırır (runtime'da, .env'e kaydetmez)"""
        try:
            user_id = int(user_id)
            if user_id in self.global_admin_ids:
                self.global_admin_ids.remove(user_id)
                logger.info(f"Global admin kaldırıldı: {user_id}")
                return True
            return False
        except (ValueError, TypeError):
            return False

# Global instance
admin_manager = AdminManager()