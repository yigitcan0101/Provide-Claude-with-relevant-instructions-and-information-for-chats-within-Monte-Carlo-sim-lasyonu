"""
Risk hesaplama ve yönetim modülü
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, List

from utils.logger import logger
from config.settings import STRATEGY_CONFIG


class RiskCalculator:
    """
    Risk metrikleri ve Kelly Criterion hesaplamaları
    """

    def __init__(self):
        """
        RiskCalculator başlatıcı
        """
        self.kelly_fraction = STRATEGY_CONFIG['kelly_fraction']
        logger.info("RiskCalculator başlatıldı")

    def calculate_risk_reward(
            self,
            entry_price: float,
            stop_loss: float,
            target_price: float
    ) -> Dict[str, float]:
        """
        Risk/Reward oranını hesapla

        Args:
            entry_price: Giriş fiyatı
            stop_loss: Stop-loss fiyatı
            target_price: Hedef fiyat

        Returns:
            dict: R:R bilgileri
        """
        risk = entry_price - stop_loss
        reward = target_price - entry_price

        if risk <= 0:
            logger.error("Risk sıfır veya negatif!")
            return {
                'risk': 0,
                'reward': 0,
                'ratio': 0,
                'error': 'Invalid risk'
            }

        ratio = reward / risk

        result = {
            'risk': float(risk),
            'reward': float(reward),
            'ratio': float(ratio),
            'risk_pct': float((risk / entry_price) * 100),
            'reward_pct': float((reward / entry_price) * 100),
        }

        logger.info(f"R:R Oranı: 1:{ratio:.2f} (Risk=${risk:.2f}, Reward=${reward:.2f})")
        return result

    def kelly_criterion(
            self,
            win_rate: float,
            avg_win: float,
            avg_loss: float
    ) -> float:
        """
        Kelly Criterion ile optimal pozisyon boyutu hesapla

        Formula: f* = (p * b - q) / b
        - p: Kazanma olasılığı
        - q: Kaybetme olasılığı (1 - p)
        - b: Ortalama kazanç / Ortalama kayıp

        Args:
            win_rate: Kazanma oranı (0-1 arası)
            avg_win: Ortalama kazanç
            avg_loss: Ortalama kayıp (pozitif değer)

        Returns:
            float: Önerilen pozisyon boyutu (0-1 arası)
        """
        if win_rate <= 0 or win_rate >= 1:
            logger.error(f"Geçersiz win_rate: {win_rate}")
            return 0.0

        if avg_win <= 0 or avg_loss <= 0:
            logger.error("Ortalama kazanç/kayıp pozitif olmalı")
            return 0.0

        p = win_rate
        q = 1 - win_rate
        b = avg_win / avg_loss

        # Kelly yüzdesi
        kelly_pct = (p * b - q) / b

        # Negatif ise trade yapma
        if kelly_pct <= 0:
            logger.warning("Kelly negatif - bu trade önerilmiyor")
            return 0.0

        # Konservatif yaklaşım: Kelly'nin %50'si (Half-Kelly)
        conservative_kelly = kelly_pct * self.kelly_fraction

        # Maksimum %25 ile sınırla
        conservative_kelly = min(conservative_kelly, 0.25)

        logger.info(
            f"Kelly Criterion: {kelly_pct:.2%} "
            f"(Konservatif: {conservative_kelly:.2%})"
        )

        return float(conservative_kelly)

    def calculate_var(
            self,
            returns: pd.Series,
            confidence_level: float = 0.95
    ) -> float:
        """
        Value at Risk (VaR) hesapla

        Args:
            returns: Getiri serisi
            confidence_level: Güven seviyesi (varsayılan: %95)

        Returns:
            float: VaR değeri (negatif = kayıp)
        """
        # Percentile hesapla
        var = np.percentile(returns, (1 - confidence_level) * 100)

        logger.info(f"VaR (%{confidence_level*100}): {var:.2%}")
        return float(var)

    def calculate_cvar(
            self,
            returns: pd.Series,
            confidence_level: float = 0.95
    ) -> float:
        """
        Conditional VaR (CVaR / Expected Shortfall) hesapla
        VaR'ı aşan kayıpların ortalaması

        Args:
            returns: Getiri serisi
            confidence_level: Güven seviyesi

        Returns:
            float: CVaR değeri
        """
        var = self.calculate_var(returns, confidence_level)

        # VaR'dan daha kötü olan getiriler
        tail_losses = returns[returns <= var]

        if len(tail_losses) == 0:
            return var

        cvar = tail_losses.mean()

        logger.info(f"CVaR (%{confidence_level*100}): {cvar:.2%}")
        return float(cvar)

    def calculate_sharpe_ratio(
            self,
            returns: pd.Series,
            risk_free_rate: float = 0.02,
            periods_per_year: int = 252
    ) -> float:
        """
        Sharpe Ratio hesapla

        Args:
            returns: Günlük getiri serisi
            risk_free_rate: Risksiz faiz oranı (yıllık)
            periods_per_year: Yılda dönem sayısı (252 = trading days)

        Returns:
            float: Sharpe Ratio
        """
        # Yıllıklandır
        mean_return = returns.mean() * periods_per_year
        std_return = returns.std() * np.sqrt(periods_per_year)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - risk_free_rate) / std_return

        logger.info(f"Sharpe Ratio: {sharpe:.4f}")
        return float(sharpe)

    def calculate_sortino_ratio(
            self,
            returns: pd.Series,
            risk_free_rate: float = 0.02,
            periods_per_year: int = 252
    ) -> float:
        """
        Sortino Ratio hesapla (sadece aşağı yönlü volatilite)

        Args:
            returns: Günlük getiri serisi
            risk_free_rate: Risksiz faiz oranı
            periods_per_year: Yılda dönem sayısı

        Returns:
            float: Sortino Ratio
        """
        # Yıllıklandır
        mean_return = returns.mean() * periods_per_year

        # Sadece negatif getiriler
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0:
            return float('inf')  # Hiç kayıp yok

        downside_std = downside_returns.std() * np.sqrt(periods_per_year)

        if downside_std == 0:
            return 0.0

        sortino = (mean_return - risk_free_rate) / downside_std

        logger.info(f"Sortino Ratio: {sortino:.4f}")
        return float(sortino)

    def calculate_max_drawdown(
            self,
            prices: pd.Series
    ) -> Dict[str, any]:
        """
        Maksimum Drawdown hesapla

        Args:
            prices: Fiyat serisi

        Returns:
            dict: Max drawdown bilgileri
        """
        # Kümülatif maksimum
        cummax = prices.cummax()

        # Drawdown (mevcut fiyat / en yüksek fiyat - 1)
        drawdown = (prices / cummax) - 1

        # Maksimum drawdown
        max_dd = drawdown.min()

        # Max DD'nin olduğu tarih
        max_dd_date = drawdown.idxmin()

        # Max DD öncesi tepe
        peak_date = cummax[:max_dd_date].idxmax()

        result = {
            'max_drawdown': float(max_dd),
            'max_drawdown_pct': float(max_dd * 100),
            'peak_date': peak_date,
            'trough_date': max_dd_date,
        }

        logger.info(f"Max Drawdown: {max_dd:.2%}")
        return result

    def position_heat_map(
            self,
            capital: float,
            positions: List[Dict]
    ) -> Dict[str, any]:
        """
        Pozisyon risk haritası (her pozisyonun portföy riskine katkısı)

        Args:
            capital: Toplam sermaye
            positions: Pozisyon listesi [{'asset': 'XAG', 'value': 1000, 'volatility': 0.25}]

        Returns:
            dict: Risk haritası
        """
        total_risk = 0
        risk_contributions = []

        for pos in positions:
            value = pos['value']
            volatility = pos['volatility']

            # Pozisyonun risk katkısı
            position_risk = value * volatility

            # Portföy içindeki ağırlık
            weight = value / capital

            risk_contributions.append({
                'asset': pos['asset'],
                'value': value,
                'weight': weight * 100,
                'volatility': volatility * 100,
                'risk_contribution': position_risk,
                'risk_contribution_pct': (position_risk / capital) * 100,
            })

            total_risk += position_risk

        # Risk oranı
        total_risk_pct = (total_risk / capital) * 100

        result = {
            'total_capital': capital,
            'total_risk': total_risk,
            'total_risk_pct': total_risk_pct,
            'positions': risk_contributions,
        }

        logger.info(f"Portföy risk oranı: {total_risk_pct:.2%}")
        return result