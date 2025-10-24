"""
İstatistiksel hesaplama motoru
"""
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict

from utils.logger import logger
from config.settings import MONTE_CARLO_CONFIG


class StatisticalEngine:
    """
    İstatistiksel analiz motoru
    """

    def __init__(self):
        """
        StatisticalEngine başlatıcı
        """
        self.trading_days_per_year = MONTE_CARLO_CONFIG['trading_days_per_year']
        logger.info("StatisticalEngine başlatıldı")

    def calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Günlük getirileri hesapla

        Args:
            data: Fiyat verisi

        Returns:
            pd.DataFrame: Returns kolonu eklenmiş veri
        """
        data = data.copy()

        # Basit getiri
        data['Returns'] = data['Close'].pct_change()

        # İlk satırdaki NaN'i kaldır
        data = data.dropna(subset=['Returns'])

        logger.info(f"Günlük getiri hesaplandı: {len(data)} satır")
        return data

    def calculate_log_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Logaritmik getirileri hesapla (Monte Carlo için)

        Args:
            data: Fiyat verisi

        Returns:
            pd.DataFrame: Log_Returns kolonu eklenmiş veri
        """
        data = data.copy()

        # Logaritmik getiri
        data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))

        # NaN'leri temizle
        data = data.dropna(subset=['Log_Returns'])

        logger.info(f"Logaritmik getiri hesaplandı: {len(data)} satır")
        return data

    def calculate_daily_statistics(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Günlük getiri istatistikleri

        Args:
            data: Fiyat verisi (Returns kolonu olmalı)

        Returns:
            dict: İstatistikler (μ, σ)
        """
        # Eğer Returns kolonu yoksa hesapla
        if 'Returns' not in data.columns:
            data = self.calculate_returns(data)

        returns = data['Returns'].dropna()

        stats = {
            'mean_daily_return': float(returns.mean()),
            'std_daily_return': float(returns.std()),
            'min_daily_return': float(returns.min()),
            'max_daily_return': float(returns.max()),
            'median_daily_return': float(returns.median()),
        }

        logger.info(f"Günlük istatistikler: μ={stats['mean_daily_return']:.6f}, σ={stats['std_daily_return']:.6f}")
        return stats

    def calculate_log_statistics(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Logaritmik getiri istatistikleri (Monte Carlo için)

        Args:
            data: Fiyat verisi (Log_Returns olmalı)

        Returns:
            dict: İstatistikler
        """
        # Eğer Log_Returns kolonu yoksa hesapla
        if 'Log_Returns' not in data.columns:
            data = self.calculate_log_returns(data)

        log_returns = data['Log_Returns'].dropna()

        stats = {
            'mean_log_return': float(log_returns.mean()),
            'std_log_return': float(log_returns.std()),
        }

        logger.info(f"Log istatistikler: μ={stats['mean_log_return']:.6f}, σ={stats['std_log_return']:.6f}")
        return stats

    def annualize_statistics(self, daily_stats: Dict[str, float]) -> Dict[str, float]:
        """
        Günlük istatistikleri yıllıklandır

        Args:
            daily_stats: Günlük istatistikler

        Returns:
            dict: Yıllıklandırılmış istatistikler
        """
        annual_stats = {
            'annual_return': daily_stats['mean_daily_return'] * self.trading_days_per_year,
            'annual_volatility': daily_stats['std_daily_return'] * np.sqrt(self.trading_days_per_year),
        }

        logger.info(
            f"Yıllık istatistikler: "
            f"Return={annual_stats['annual_return']:.2%}, "
            f"Volatilite={annual_stats['annual_volatility']:.2%}"
        )
        return annual_stats

    def calculate_correlation(
            self,
            data1: pd.DataFrame,
            data2: pd.DataFrame
    ) -> float:
        """
        İki asset arasındaki korelasyon

        Args:
            data1: İlk asset verisi
            data2: İkinci asset verisi

        Returns:
            float: Korelasyon katsayısı
        """
        # Her iki veriyi de aynı tarihlere hizala
        merged = pd.merge(
            data1[['Close']],
            data2[['Close']],
            left_index=True,
            right_index=True,
            suffixes=('_1', '_2')
        )

        # Korelasyon hesapla
        correlation = float(merged['Close_1'].corr(merged['Close_2']))

        logger.info(f"Korelasyon: {correlation:.4f}")
        return correlation

    def calculate_sharpe_ratio(
            self,
            returns: pd.Series,
            risk_free_rate: float = 0.02
    ) -> float:
        """
        Sharpe Ratio hesapla

        Args:
            returns: Getiri serisi
            risk_free_rate: Risksiz faiz oranı (varsayılan %2)

        Returns:
            float: Sharpe Ratio
        """
        mean_return = returns.mean() * self.trading_days_per_year
        std_return = returns.std() * np.sqrt(self.trading_days_per_year)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - risk_free_rate) / std_return

        logger.info(f"Sharpe Ratio: {sharpe:.4f}")
        return float(sharpe)

    def get_full_statistics(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Tüm istatistikleri toplu olarak hesapla

        Args:
            data: Fiyat verisi

        Returns:
            dict: Tüm istatistikler
        """
        # Getirileri hesapla
        data_with_returns = self.calculate_returns(data)
        data_with_log = self.calculate_log_returns(data)

        # Günlük istatistikler
        daily_stats = self.calculate_daily_statistics(data_with_returns)

        # Log istatistikler
        log_stats = self.calculate_log_statistics(data_with_log)

        # Yıllık istatistikler
        annual_stats = self.annualize_statistics(daily_stats)

        # Sharpe Ratio
        sharpe = self.calculate_sharpe_ratio(data_with_returns['Returns'])

        # Tüm istatistikleri birleştir
        full_stats = {
            **daily_stats,
            **log_stats,
            **annual_stats,
            'sharpe_ratio': sharpe,
            'current_price': float(data['Close'].iloc[-1]),
            'data_points': len(data),
        }

        logger.info("Tüm istatistikler hesaplandı")
        return full_stats