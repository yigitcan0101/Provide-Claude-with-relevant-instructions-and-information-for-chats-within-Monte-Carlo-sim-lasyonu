"""
Portföy optimizasyonu ve Kelly Criterion
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

from utils.logger import logger
from strategy.risk_calculator import RiskCalculator


class PortfolioOptimizer:
    """
    Modern Portfolio Theory + Kelly Criterion
    """

    def __init__(self):
        """
        PortfolioOptimizer başlatıcı
        """
        self.risk_calc = RiskCalculator()
        logger.info("PortfolioOptimizer başlatıldı")

    def calculate_optimal_allocation(
            self,
            returns_dict: Dict[str, pd.Series],
            risk_free_rate: float = 0.02
    ) -> Dict[str, any]:
        """
        Optimal portföy dağılımı (Sharpe Ratio maksimizasyonu)

        Args:
            returns_dict: {'asset': returns_series}
            risk_free_rate: Risksiz faiz

        Returns:
            dict: Optimal ağırlıklar
        """
        assets = list(returns_dict.keys())
        returns_df = pd.DataFrame(returns_dict)

        # Beklenen getiriler (yıllık)
        expected_returns = returns_df.mean() * 252

        # Kovaryans matrisi (yıllık)
        cov_matrix = returns_df.cov() * 252

        # Basit Equal-Weight başlangıç
        n_assets = len(assets)
        weights = np.array([1 / n_assets] * n_assets)

        # Portfolio metrikleri
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility

        allocation = {
            'assets': assets,
            'weights': {asset: float(w) for asset, w in zip(assets, weights)},
            'expected_return': float(portfolio_return),
            'volatility': float(portfolio_volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'method': 'Equal-Weight (Simplified)',
        }

        logger.info(
            f"Optimal allocation: Sharpe={sharpe_ratio:.4f}, "
            f"Return={portfolio_return:.2%}"
        )

        return allocation

    def kelly_position_sizing(
            self,
            win_rate: float,
            avg_win_pct: float,
            avg_loss_pct: float,
            max_position: float = 0.25
    ) -> float:
        """
        Kelly Criterion pozisyon boyutu

        Args:
            win_rate: Kazanma oranı
            avg_win_pct: Ortalama kazanç %
            avg_loss_pct: Ortalama kayıp %
            max_position: Maksimum pozisyon (varsayılan: %25)

        Returns:
            float: Önerilen pozisyon boyutu
        """
        kelly = self.risk_calc.kelly_criterion(
            win_rate=win_rate,
            avg_win=avg_win_pct,
            avg_loss=avg_loss_pct
        )

        # Maksimum ile sınırla
        kelly = min(kelly, max_position)

        logger.info(f"Kelly position size: {kelly:.2%}")
        return float(kelly)

    def diversification_score(
            self,
            returns_dict: Dict[str, pd.Series]
    ) -> Dict[str, float]:
        """
        Portföy çeşitlendirme skoru

        Args:
            returns_dict: Asset getirileri

        Returns:
            dict: Çeşitlendirme metrikleri
        """
        returns_df = pd.DataFrame(returns_dict)

        # Korelasyon matrisi
        corr_matrix = returns_df.corr()

        # Ortalama korelasyon
        avg_correlation = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()

        # Diversification ratio (1 = mükemmel çeşitli, 0 = hiç çeşitli değil)
        div_ratio = 1 - abs(avg_correlation)

        score = {
            'average_correlation': float(avg_correlation),
            'diversification_ratio': float(div_ratio),
            'interpretation': self._interpret_diversification(div_ratio),
        }

        logger.info(f"Diversification score: {div_ratio:.2f}")
        return score

    def _interpret_diversification(self, ratio: float) -> str:
        """Çeşitlendirme yorumlama"""
        if ratio > 0.7:
            return "Mükemmel çeşitlendirme"
        elif ratio > 0.5:
            return "İyi çeşitlendirme"
        elif ratio > 0.3:
            return "Orta çeşitlendirme"
        else:
            return "Zayıf çeşitlendirme"