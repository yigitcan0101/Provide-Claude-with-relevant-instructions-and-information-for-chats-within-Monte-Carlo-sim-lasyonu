"""
Performans metrikleri
"""
import pandas as pd
import numpy as np
from typing import Dict, List

from utils.logger import logger


class PerformanceMetrics:
    """
    Backtest performans metrikleri
    """

    def __init__(self):
        """
        PerformanceMetrics başlatıcı
        """
        logger.info("PerformanceMetrics başlatıldı")

    def calculate_sharpe_ratio(
            self,
            equity_curve: List[float],
            risk_free_rate: float = 0.02
    ) -> float:
        """
        Sharpe Ratio hesapla
        """
        returns = pd.Series(equity_curve).pct_change().dropna()

        mean_return = returns.mean() * 252
        std_return = returns.std() * np.sqrt(252)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - risk_free_rate) / std_return
        return float(sharpe)

    def calculate_max_drawdown(
            self,
            equity_curve: List[float]
    ) -> Dict[str, float]:
        """
        Maximum Drawdown hesapla
        """
        equity = pd.Series(equity_curve)
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax

        max_dd = drawdown.min()

        return {
            'max_drawdown': float(max_dd),
            'max_drawdown_pct': float(max_dd * 100)
        }

    def calculate_calmar_ratio(
            self,
            total_return: float,
            max_drawdown: float
    ) -> float:
        """
        Calmar Ratio (Return / Max DD)
        """
        if max_drawdown == 0:
            return 0.0

        calmar = abs(total_return / max_drawdown)
        return float(calmar)

    def calculate_profit_factor(
            self,
            trades: List[Dict]
    ) -> float:
        """
        Profit Factor (Kazançlar / Kayıplar)
        """
        trades_df = pd.DataFrame(trades)

        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())

        if gross_loss == 0:
            return float('inf')

        profit_factor = gross_profit / gross_loss
        return float(profit_factor)

    def get_all_metrics(
            self,
            backtest_results: Dict
    ) -> Dict[str, any]:
        """
        Tüm metrikleri hesapla
        """
        sharpe = self.calculate_sharpe_ratio(backtest_results['equity_curve'])
        max_dd = self.calculate_max_drawdown(backtest_results['equity_curve'])
        calmar = self.calculate_calmar_ratio(
            backtest_results['total_return'],
            max_dd['max_drawdown']
        )
        profit_factor = self.calculate_profit_factor(backtest_results['trades'])

        metrics = {
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd['max_drawdown'],
            'max_drawdown_pct': max_dd['max_drawdown_pct'],
            'calmar_ratio': calmar,
            'profit_factor': profit_factor,
        }

        logger.info("Tüm metrikler hesaplandı")
        return metrics