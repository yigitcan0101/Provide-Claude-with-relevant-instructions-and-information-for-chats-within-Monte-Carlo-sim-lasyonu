"""
Veri önbellekleme modülü
"""
import pickle
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional

from config.settings import CACHE_DIR, DATA_CONFIG
from utils.logger import logger


class CacheManager:
    """
    Veri önbellekleme yöneticisi
    """

    def __init__(self):
        """
        CacheManager başlatıcı
        """
        self.cache_dir = CACHE_DIR
        self.cache_duration_hours = DATA_CONFIG['cache_duration_hours']

        # Cache dizinini oluştur
        self.cache_dir.mkdir(exist_ok=True)

        logger.info(f"CacheManager başlatıldı: {self.cache_dir}")

    def _generate_cache_key(self, asset_name: str, period: str) -> str:
        """
        Cache anahtarı oluştur

        Args:
            asset_name: Asset adı
            period: Zaman periyodu

        Returns:
            str: Cache dosya adı
        """
        key = f"{asset_name}_{period}"
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return f"{hash_key}.pkl"

    def save_to_cache(
            self,
            data: pd.DataFrame,
            asset_name: str,
            period: str
    ) -> bool:
        """
        Veriyi önbelleğe kaydet

        Args:
            data: Kaydedilecek veri
            asset_name: Asset adı
            period: Zaman periyodu

        Returns:
            bool: Başarılı ise True
        """
        try:
            cache_file = self.cache_dir / self._generate_cache_key(asset_name, period)

            cache_data = {
                'timestamp': datetime.now(),
                'asset_name': asset_name,
                'period': period,
                'data': data
            }

            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)

            logger.info(f"Veri önbelleğe kaydedildi: {cache_file.name}")
            return True

        except Exception as e:
            logger.error(f"Cache kaydetme hatası: {str(e)}")
            return False

    def load_from_cache(
            self,
            asset_name: str,
            period: str
    ) -> Optional[pd.DataFrame]:
        """
        Önbellekten veri yükle

        Args:
            asset_name: Asset adı
            period: Zaman periyodu

        Returns:
            pd.DataFrame: Cache'den yüklenen veri veya None
        """
        try:
            cache_file = self.cache_dir / self._generate_cache_key(asset_name, period)

            if not cache_file.exists():
                logger.debug(f"Cache bulunamadı: {cache_file.name}")
                return None

            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)

            # Cache geçerlilik kontrolü
            cache_age = datetime.now() - cache_data['timestamp']
            max_age = timedelta(hours=self.cache_duration_hours)

            if cache_age > max_age:
                logger.info(f"Cache süresi dolmuş: {cache_age} > {max_age}")
                return None

            logger.info(f"Veri cache'den yüklendi: {cache_file.name}")
            return cache_data['data']

        except Exception as e:
            logger.error(f"Cache yükleme hatası: {str(e)}")
            return None

    def is_cache_valid(
            self,
            asset_name: str,
            period: str
    ) -> bool:
        """
        Cache'in geçerli olup olmadığını kontrol et

        Args:
            asset_name: Asset adı
            period: Zaman periyodu

        Returns:
            bool: Geçerli ise True
        """
        cache_file = self.cache_dir / self._generate_cache_key(asset_name, period)

        if not cache_file.exists():
            return False

        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)

            cache_age = datetime.now() - cache_data['timestamp']
            max_age = timedelta(hours=self.cache_duration_hours)

            return cache_age <= max_age

        except:
            return False

    def clear_cache(self) -> bool:
        """
        Tüm cache'i temizle

        Returns:
            bool: Başarılı ise True
        """
        try:
            for cache_file in self.cache_dir.glob('*.pkl'):
                cache_file.unlink()

            logger.info("Cache temizlendi")
            return True

        except Exception as e:
            logger.error(f"Cache temizleme hatası: {str(e)}")
            return False