"""
Monte Carlo simülasyon motoru
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from scipy import stats

from utils.logger import logger
from config.settings import MONTE_CARLO_CONFIG
from analysis.statistical_engine import StatisticalEngine


class MonteCarloSimulator:
    """
    Monte Carlo fiyat simülasyonu
    """

    def __init__(self):
        """
        MonteCarloSimulator başlatıcı
        """
        self.iterations = MONTE_CARLO_CONFIG['iterations']
        self.trading_days = MONTE_CARLO_CONFIG['trading_days_per_year']
        self.projection_days = MONTE_CARLO_CONFIG['projection_days']
        self.confidence_levels = MONTE_CARLO_CONFIG['confidence_levels']

        self.stat_engine = StatisticalEngine()

        logger.info(
            f"MonteCarloSimulator başlatıldı: "
            f"{self.iterations} iterasyon, {self.projection_days} gün"
        )

    def run_simulation(
            self,
            current_price: float,
            mean_return: float,
            volatility: float,
            days: Optional[int] = None,
            iterations: Optional[int] = None
    ) -> np.ndarray:
        """
        Monte Carlo simülasyonu çalıştır

        Model: Geometric Brownian Motion
        S_t = S_0 * exp((μ - 0.5σ²)t + σ√t * Z)

        Args:
            current_price: Başlangıç fiyatı
            mean_return: Ortalama günlük log getiri
            volatility: Günlük volatilite (log returns)
            days: Projeksiyon gün sayısı
            iterations: İterasyon sayısı

        Returns:
            np.ndarray: Simülasyon sonuçları (iterations x days)
        """
        days = days or self.projection_days
        iterations = iterations or self.iterations

        logger.info(f"Simülasyon başlıyor: {iterations} iterasyon x {days} gün")

        # Drift terimi (μ - 0.5σ²)
        drift = mean_return - 0.5 * volatility ** 2

        # Rastgele sayılar (standart normal dağılım)
        random_shocks = np.random.standard_normal((iterations, days))

        # Fiyat yolları hesapla
        # Her gün için: S_t = S_{t-1} * exp(drift + volatility * Z_t)
        daily_returns = np.exp(drift + volatility * random_shocks)

        # Kümülatif çarpım ile fiyat yolu oluştur
        price_paths = np.zeros_like(daily_returns)
        price_paths[:, 0] = current_price * daily_returns[:, 0]

        for t in range(1, days):
            price_paths[:, t] = price_paths[:, t - 1] * daily_returns[:, t]

        logger.info("Simülasyon tamamlandı")
        return price_paths

    def analyze_simulation_results(
            self,
            price_paths: np.ndarray,
            current_price: float
    ) -> Dict[str, any]:
        """
        Simülasyon sonuçlarını analiz et

        Args:
            price_paths: Simülasyon sonuçları
            current_price: Başlangıç fiyatı

        Returns:
            dict: Analiz sonuçları
        """
        # Son gün fiyatları
        final_prices = price_paths[:, -1]

        # Percentile'ları hesapla
        percentiles = {}
        for level in self.confidence_levels:
            percentile_value = np.percentile(final_prices, level * 100)
            percentiles[f'percentile_{int(level * 100)}'] = float(percentile_value)

        # İstatistikler
        results = {
            'mean_final_price': float(np.mean(final_prices)),
            'median_final_price': float(np.median(final_prices)),
            'std_final_price': float(np.std(final_prices)),
            'min_final_price': float(np.min(final_prices)),
            'max_final_price': float(np.max(final_prices)),
            **percentiles,
            'current_price': current_price,
            'iterations': price_paths.shape[0],
            'days': price_paths.shape[1],
        }

        logger.info(
            f"Simülasyon analizi: "
            f"Medyan=${results['median_final_price']:.2f}, "
            f"Aralık=${results['percentile_5']:.2f}-${results['percentile_95']:.2f}"
        )

        return results

    def calculate_target_probability(
            self,
            price_paths: np.ndarray,
            target_price: float
    ) -> float:
        """
        Belirli bir fiyata ulaşma olasılığı

        Args:
            price_paths: Simülasyon sonuçları
            target_price: Hedef fiyat

        Returns:
            float: Olasılık (0-1 arası)
        """
        final_prices = price_paths[:, -1]
        above_target = np.sum(final_prices >= target_price)
        probability = above_target / len(final_prices)

        logger.info(f"${target_price:.2f} hedefine ulaşma olasılığı: {probability:.2%}")
        return float(probability)

    def calculate_var(
            self,
            price_paths: np.ndarray,
            confidence_level: float = 0.05
    ) -> float:
        """
        Value at Risk (VaR) hesapla

        Args:
            price_paths: Simülasyon sonuçları
            confidence_level: Güven seviyesi (varsayılan %5)

        Returns:
            float: VaR değeri
        """
        final_prices = price_paths[:, -1]
        current_price = price_paths[:, 0].mean()

        # Fiyat değişimi
        price_changes = final_prices - current_price

        # VaR hesapla
        var = np.percentile(price_changes, confidence_level * 100)

        logger.info(f"VaR (%{confidence_level * 100}): ${var:.2f}")
        return float(var)

    def run_full_analysis(
            self,
            data: pd.DataFrame,
            target_price: Optional[float] = None,
            custom_days: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Tam Monte Carlo analizi (veriyi al, simülasyon yap, analiz et)

        Args:
            data: Fiyat verisi
            target_price: Hedef fiyat (opsiyonel - kullanıcı belirler)
            custom_days: Özel projeksiyon gün sayısı

        Returns:
            dict: Tüm sonuçlar
        """
        logger.info("Tam Monte Carlo analizi başlıyor...")

        # Multi-index düzleştir
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # İstatistikleri hesapla
        stats = self.stat_engine.get_full_statistics(data)

        # Simülasyon parametreleri
        current_price = stats['current_price']
        mean_return = stats['mean_log_return']
        volatility = stats['std_log_return']

        # Simülasyon çalıştır
        price_paths = self.run_simulation(
            current_price=current_price,
            mean_return=mean_return,
            volatility=volatility,
            days=custom_days
        )

        # Sonuçları analiz et
        results = self.analyze_simulation_results(price_paths, current_price)

        # Hedef fiyat ANALİZİ (SADECE kullanıcı belirtirse)
        if target_price:
            target_probability = self.calculate_target_probability(
                price_paths, target_price
            )
            results['target_analysis'] = {
                'target_price': target_price,
                'probability': target_probability,
                'user_defined': True  # Kullanıcı tarafından belirlendi
            }
            logger.info(f"Kullanıcı hedef fiyatı: ${target_price:.2f} - Olasılık: {target_probability:.2%}")
        else:
            # Hedef fiyat belirtilmemişse, percentile'ları hedef olarak göster
            results['target_analysis'] = {
                'percentile_50_target': results['percentile_50'],
                'percentile_75_target': np.percentile(price_paths[:, -1], 75),
                'percentile_90_target': np.percentile(price_paths[:, -1], 90),
                'user_defined': False  # Sistem önerisi
            }
            logger.info("Hedef fiyat belirtilmedi, percentile hedefleri hesaplandı")

        # VaR hesapla
        results['risk_metrics'] = {
            'var_5': self.calculate_var(price_paths, 0.05),
            'var_1': self.calculate_var(price_paths, 0.01),
        }

        # İstatistikleri ekle
        results['statistics'] = stats

        # Fiyat yollarını da ekle (grafik için)
        results['price_paths'] = price_paths

        logger.info("Monte Carlo analizi tamamlandı")
        return results