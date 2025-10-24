"""
Trade simülatörü
"""
import pandas as pd
from typing import Dict, List
from datetime import datetime

from utils.logger import logger


class TradeSimulator:
    """
    Tekil trade simülasyonu
    """

    def __init__(self, commission: float = 0.001, slippage: float = 0.0005):
        """
        TradeSimulator başlatıcı
        """
        self.commission = commission
        self.slippage = slippage
        logger.info("TradeSimulator başlatıldı")

    def simulate_trade(
            self,
            entry_price: float,
            exit_price: float,
            shares: float,
            trade_type: str = 'long'
    ) -> Dict[str, float]:
        """
        Tek bir trade simüle et

        Args:
            entry_price: Giriş fiyatı
            exit_price: Çıkış fiyatı
            shares: Hisse sayısı
            trade_type: 'long' veya 'short'

        Returns:
            dict: Trade sonucu
        """
        # Slippage uygula
        actual_entry = entry_price * (1 + self.slippage if trade_type == 'long' else 1 - self.slippage)
        actual_exit = exit_price * (1 - self.slippage if trade_type == 'long' else 1 + self.slippage)

        # Komisyon
        entry_commission = actual_entry * shares * self.commission
        exit_commission = actual_exit * shares * self.commission

        # P/L hesapla
        if trade_type == 'long':
            gross_pnl = (actual_exit - actual_entry) * shares
        else:  # short
            gross_pnl = (actual_entry - actual_exit) * shares

        net_pnl = gross_pnl - entry_commission - exit_commission

        result = {
            'gross_pnl': float(gross_pnl),
            'net_pnl': float(net_pnl),
            'commission_paid': float(entry_commission + exit_commission),
            'return_pct': float((actual_exit - actual_entry) / actual_entry * 100),
        }

        return result