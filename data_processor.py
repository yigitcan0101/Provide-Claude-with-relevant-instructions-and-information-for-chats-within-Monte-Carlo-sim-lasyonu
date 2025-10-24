"""
Veri işleme ve temizleme modülü
"""
import pandas as pd
import numpy as np
from typing import Optional

from utils.logger import logger
from utils.helpers import clean_dataframe


class DataProcessor:
    """
    Veri işleme sınıfı
    """

    def __init__(self):
        """
        DataProcessor başlatıcı
        """
        logger.info("DataProcessor başlatıldı")

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Veriyi temizle (NaN, duplicate, vb.)

        Args:
            data: Ham veri

        Returns:
            pd.DataFrame: Temizlenmiş veri
        """
        logger.info("Veri temizleniyor...")
        return clean_dataframe(data)

    def calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Günlük getiri hesapla

        Args:
            data: Fiyat verisi

        Returns:
            pd.DataFrame: Returns kolonu eklenmiş veri
        """
        data = data.copy()

        # Basit getiri
        data['Returns'] = data['Close'].pct_change()

        logger.info("Günlük getiri hesaplandı")
        return data

    def calculate_log_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Logaritmik getiri hesapla (Monte Carlo için)

        Args:
            data: Fiyat verisi

        Returns:
            pd.DataFrame: Log_Returns kolonu eklenmiş veri
        """
        data = data.copy()

        # Logaritmik getiri
        data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))

        logger.info("Logaritmik getiri hesaplandı")
        return data

    def resample_data(
            self,
            data: pd.DataFrame,
            frequency: str = 'D'
    ) -> pd.DataFrame:
        """
        Veriyi yeniden örnekle (günlük/haftalık/aylık)

        Args:
            data: Fiyat verisi
            frequency: 'D' (günlük), 'W' (haftalık), 'M' (aylık)

        Returns:
            pd.DataFrame: Yeniden örneklenmiş veri
        """
        resampled = data.resample(frequency).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })

        logger.info(f"Veri yeniden örneklendi: {frequency}")
        return resampled.dropna()

    def add_moving_averages(
            self,
            data: pd.DataFrame,
            windows: list[int] = [20, 50, 200]
    ) -> pd.DataFrame:
        """
        Hareketli ortalamalar ekle

        Args:
            data: Fiyat verisi
            windows: MA periyotları

        Returns:
            pd.DataFrame: MA kolonları eklenmiş veri
        """
        data = data.copy()

        for window in windows:
            data[f'MA{window}'] = data['Close'].rolling(window=window).mean()

        logger.info(f"Hareketli ortalamalar eklendi: {windows}")
        return data

    def normalize_prices(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Fiyatları normalize et (0-1 arası)

        Args:
            data: Fiyat verisi

        Returns:
            pd.DataFrame: Normalize_Close kolonu eklenmiş veri
        """
        data = data.copy()

        min_price = data['Close'].min()
        max_price = data['Close'].max()

        data['Normalized_Close'] = (data['Close'] - min_price) / (max_price - min_price)

        logger.info("Fiyatlar normalize edildi")
        return data

    def get_price_statistics(self, data: pd.DataFrame) -> dict:
        """
        Fiyat istatistikleri hesapla

        Args:
            data: Fiyat verisi

        Returns:
            dict: İstatistikler
        """
        stats = {
            'count': len(data),
            'current_price': data['Close'].iloc[-1],
            'mean_price': data['Close'].mean(),
            'median_price': data['Close'].median(),
            'std_price': data['Close'].std(),
            'min_price': data['Close'].min(),
            'max_price': data['Close'].max(),
            'min_date': data['Close'].idxmin(),
            'max_date': data['Close'].idxmax(),
        }

        logger.info("Fiyat istatistikleri hesaplandı")
        return stats