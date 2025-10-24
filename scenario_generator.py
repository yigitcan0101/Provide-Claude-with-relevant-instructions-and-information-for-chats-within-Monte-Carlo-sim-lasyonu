"""
Bull/Base/Bear senaryo oluşturucu
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

from utils.logger import logger
from analysis.monte_carlo_simulator import MonteCarloSimulator
from analysis.statistical_engine import StatisticalEngine


class ScenarioGenerator:
    """
    Bull, Base, Bear senaryoları oluşturur
    """

    def __init__(self):
        """
        ScenarioGenerator başlatıcı
        """
        self.mc_simulator = MonteCarloSimulator()
        self.stat_engine = StatisticalEngine()
        logger.info("ScenarioGenerator başlatıldı")

    def generate_scenarios(
            self,
            data: pd.DataFrame,
            projection_days: int = 252
    ) -> Dict[str, any]:
        """
        3 senaryo oluştur: Bull, Base, Bear

        Args:
            data: Fiyat verisi
            projection_days: Projeksiyon günü

        Returns:
            dict: Tüm senaryolar
        """
        # İstatistikleri hesapla
        stats = self.stat_engine.get_full_statistics(data)

        current_price = stats['current_price']
        mean_return = stats['mean_log_return']
        volatility = stats['std_log_return']

        # BASE SENARYO (Mevcut trend devam eder)
        base_scenario = self._create_base_scenario(
            current_price, mean_return, volatility, projection_days
        )

        # BULL SENARYO (Yükseliş: μ + 0.5σ)
        bull_scenario = self._create_bull_scenario(
            current_price, mean_return, volatility, projection_days
        )

        # BEAR SENARYO (Düşüş: μ - 0.5σ)
        bear_scenario = self._create_bear_scenario(
            current_price, mean_return, volatility, projection_days
        )

        results = {
            'current_price': current_price,
            'projection_days': projection_days,
            'base_scenario': base_scenario,
            'bull_scenario': bull_scenario,
            'bear_scenario': bear_scenario,
            'statistics': stats,
        }

        logger.info("3 senaryo oluşturuldu (Base, Bull, Bear)")
        return results

    def _create_base_scenario(
            self,
            current_price: float,
            mean_return: float,
            volatility: float,
            days: int
    ) -> Dict[str, any]:
        """
        Base senaryo (mevcut trend)
        """
        # Monte Carlo simülasyonu
        price_paths = self.mc_simulator.run_simulation(
            current_price=current_price,
            mean_return=mean_return,
            volatility=volatility,
            days=days,
            iterations=1000
        )

        final_prices = price_paths[:, -1]

        scenario = {
            'name': 'Base Senaryo',
            'description': 'Mevcut trend devam eder',
            'mean_return': mean_return,
            'volatility': volatility,
            'expected_price': float(np.median(final_prices)),
            'price_range': {
                'pessimistic': float(np.percentile(final_prices, 25)),
                'realistic': float(np.percentile(final_prices, 50)),
                'optimistic': float(np.percentile(final_prices, 75)),
            },
            'probability_distribution': {
                'p5': float(np.percentile(final_prices, 5)),
                'p25': float(np.percentile(final_prices, 25)),
                'p50': float(np.percentile(final_prices, 50)),
                'p75': float(np.percentile(final_prices, 75)),
                'p95': float(np.percentile(final_prices, 95)),
            }
        }

        return scenario

    def _create_bull_scenario(
            self,
            current_price: float,
            mean_return: float,
            volatility: float,
            days: int
    ) -> Dict[str, any]:
        """
        Bull senaryo (yükseliş)
        """
        # Yükseliş: Daha yüksek μ
        bull_mean = mean_return + (0.5 * volatility)

        price_paths = self.mc_simulator.run_simulation(
            current_price=current_price,
            mean_return=bull_mean,
            volatility=volatility,
            days=days,
            iterations=1000
        )

        final_prices = price_paths[:, -1]

        scenario = {
            'name': 'Bull Senaryo',
            'description': 'Güçlü yükseliş trendi',
            'mean_return': bull_mean,
            'volatility': volatility,
            'expected_price': float(np.median(final_prices)),
            'price_range': {
                'pessimistic': float(np.percentile(final_prices, 25)),
                'realistic': float(np.percentile(final_prices, 50)),
                'optimistic': float(np.percentile(final_prices, 75)),
            },
            'probability_distribution': {
                'p5': float(np.percentile(final_prices, 5)),
                'p25': float(np.percentile(final_prices, 25)),
                'p50': float(np.percentile(final_prices, 50)),
                'p75': float(np.percentile(final_prices, 75)),
                'p95': float(np.percentile(final_prices, 95)),
            }
        }

        return scenario

    def _create_bear_scenario(
            self,
            current_price: float,
            mean_return: float,
            volatility: float,
            days: int
    ) -> Dict[str, any]:
        """
        Bear senaryo (düşüş)
        """
        # Düşüş: Daha düşük μ
        bear_mean = mean_return - (0.5 * volatility)

        price_paths = self.mc_simulator.run_simulation(
            current_price=current_price,
            mean_return=bear_mean,
            volatility=volatility,
            days=days,
            iterations=1000
        )

        final_prices = price_paths[:, -1]

        scenario = {
            'name': 'Bear Senaryo',
            'description': 'Düşüş trendi',
            'mean_return': bear_mean,
            'volatility': volatility,
            'expected_price': float(np.median(final_prices)),
            'price_range': {
                'pessimistic': float(np.percentile(final_prices, 25)),
                'realistic': float(np.percentile(final_prices, 50)),
                'optimistic': float(np.percentile(final_prices, 75)),
            },
            'probability_distribution': {
                'p5': float(np.percentile(final_prices, 5)),
                'p25': float(np.percentile(final_prices, 25)),
                'p50': float(np.percentile(final_prices, 50)),
                'p75': float(np.percentile(final_prices, 75)),
                'p95': float(np.percentile(final_prices, 95)),
            }
        }

        return scenario

    def compare_scenarios(
            self,
            scenarios: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Senaryoları karşılaştır

        Args:
            scenarios: generate_scenarios() çıktısı

        Returns:
            dict: Karşılaştırma
        """
        current = scenarios['current_price']
        base = scenarios['base_scenario']['expected_price']
        bull = scenarios['bull_scenario']['expected_price']
        bear = scenarios['bear_scenario']['expected_price']

        comparison = {
            'current_price': current,
            'base_change_pct': ((base - current) / current) * 100,
            'bull_change_pct': ((bull - current) / current) * 100,
            'bear_change_pct': ((bear - current) / current) * 100,
            'upside_potential': bull - current,
            'downside_risk': current - bear,
            'risk_reward': (bull - current) / (current - bear) if current > bear else 0,
        }

        logger.info("Senaryolar karşılaştırıldı")
        return comparison