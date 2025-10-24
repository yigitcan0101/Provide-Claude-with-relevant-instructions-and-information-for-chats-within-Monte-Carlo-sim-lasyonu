"""
Geçmiş veri yönetimi (backtest için)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict

from utils.logger import logger
from data.data_collector import DataCollector
from data.cache_manager import CacheManager


class HistoricalData:
    """
    Backtest için geçmiş veri yönetimi
    """

    def __init__(self):
        """
        HistoricalData başlatıcı
        """
        self.collector = DataCollector()
        self.cache = CacheManager()
        logger.info("HistoricalData başlatıldı")

    def get_backtest_data(
            self,
            asset_name: str,
            start_date: datetime,
            end_date: datetime
    ) -> pd.DataFrame:
        """
        Backtest için veri al

        Args:
            asset_name: Asset adı
            start_date: Başlangıç
            end_date: Bitiş

        Returns:
            pd.DataFrame: Geçmiş veri
        """
        data = self.collector.fetch_price_data(
            asset_name=asset_name,
            start_date=start_date,
            end_date=end_date
        )

        if data is None:
            logger.error("Backtest verisi alınamadı")
            return pd.DataFrame()

        logger.info(
            f"Backtest verisi: {len(data)} satır "
            f"({start_date.date()} - {end_date.date()})"
        )

        return data

    def split_train_test(
            self,
            data: pd.DataFrame,
            train_ratio: float = 0.7
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Veriyi train/test olarak böl

        Args:
            data: Tüm veri
            train_ratio: Train oranı (varsayılan: %70)

        Returns:
            tuple: (train_data, test_data)
        """
        split_index = int(len(data) * train_ratio)

        train_data = data.iloc[:split_index]
        test_data = data.iloc[split_index:]

        logger.info(
            f"Train/Test split: {len(train_data)} / {len(test_data)} satır"
        )

        return train_data, test_data

    def get_rolling_window_data(
            self,
            data: pd.DataFrame,
            window_size: int = 252
    ) -> list:
        """
        Rolling window şeklinde veri döndür

        Args:
            data: Fiyat verisi
            window_size: Pencere boyutu (varsayılan: 252 gün)

        Returns:
            list: [(window_data, next_price), ...]
        """
        windows = []

        for i in range(window_size, len(data)):
            window = data.iloc[i - window_size:i]
            next_price = data.iloc[i]['Close']

            windows.append((window, next_price))

        logger.info(f"{len(windows)} rolling window oluşturuldu")
        return windows

    def align_multiple_assets(
            self,
            asset_data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Birden fazla asset verisini tarihlere göre hizala

        Args:
            asset_data_dict: {'asset': data}

        Returns:
            dict: Hizalanmış veriler
        """
        # İlk asset'i referans al
        first_asset = list(asset_data_dict.keys())[0]
        aligned_data = {first_asset: asset_data_dict[first_asset]}

        for asset, data in list(asset_data_dict.items())[1:]:
            # İndeksleri hizala
            aligned = data.reindex(aligned_data[first_asset].index)

            # NaN'leri forward fill
            aligned = aligned.ffill().bfill()

            aligned_data[asset] = aligned

        logger.info(f"{len(asset_data_dict)} asset hizalandı")
        return aligned_data

    def create_synthetic_data(
            self,
            start_price: float,
            days: int,
            mean_return: float,
            volatility: float,
            seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Sentetik test verisi oluştur (GBM ile)

        Args:
            start_price: Başlangıç fiyatı
            days: Gün sayısı
            mean_return: Ortalama günlük getiri
            volatility: Günlük volatilite
            seed: Random seed

        Returns:
            pd.DataFrame: Sentetik veri
        """
        if seed:
            np.random.seed(seed)

        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

        # GBM simülasyonu
        returns = np.random.normal(mean_return, volatility, days)
        prices = [start_price]

        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        data = pd.DataFrame({
            'Date': dates,
            'Open': [p * 0.998 for p in prices],
            'High': [p * 1.005 for p in prices],
            'Low': [p * 0.995 for p in prices],
            'Close': prices,
            'Volume': np.random.randint(1000000, 5000000, days)
        })

        data.set_index('Date', inplace=True)

        logger.info(f"Sentetik veri oluşturuldu: {days} gün")
        return data