"""
Backtest motoru
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

from utils.logger import logger
from config.settings import BACKTEST_CONFIG
from analysis.technical_analyzer import TechnicalAnalyzer
from strategy.support_resistance import SupportResistance
from strategy.position_manager import PositionManager


class BacktestEngine:
    """
    Strateji backtest motoru
    """

    def __init__(self):
        """
        BacktestEngine başlatıcı
        """
        self.initial_capital = BACKTEST_CONFIG['initial_capital']
        self.commission = BACKTEST_CONFIG['commission']
        self.slippage = BACKTEST_CONFIG['slippage']

        self.analyzer = TechnicalAnalyzer()
        self.sr = SupportResistance()
        self.pm = PositionManager()

        logger.info(
            f"BacktestEngine başlatıldı: "
            f"Sermaye=${self.initial_capital}, "
            f"Komisyon={self.commission:.3%}"
        )

    def run_backtest(
            self,
            data: pd.DataFrame,
            strategy_name: str = 'support_resistance'
    ) -> Dict[str, any]:
        """
        Backtest çalıştır

        Args:
            data: Geçmiş fiyat verisi
            strategy_name: Strateji adı

        Returns:
            dict: Backtest sonuçları
        """
        logger.info(f"Backtest başlıyor: {strategy_name}")

        # Multi-index düzleştir
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Portföy başlangıç
        capital = self.initial_capital
        positions = []  # Açık pozisyonlar
        trades = []  # Tamamlanmış işlemler
        equity_curve = [capital]
        dates = [data.index[0]]

        # Her gün için simülasyon
        for i in range(200, len(data)):  # İlk 200 gün teknik göstergeler için
            current_date = data.index[i]
            current_data = data.iloc[:i+1]

            current_price = float(current_data['Close'].iloc[-1])

            # Teknik analiz
            tech = self.analyzer.get_full_technical_analysis(current_data)

            # Destek/Direnç
            levels = self.sr.find_support_resistance_levels(current_data)

            # AÇIK POZİSYON KONTROLÜ
            for position in positions[:]:
                # Stop-loss kontrolü
                if current_price <= position['stop_loss']:
                    # Stop-loss'a takıldı
                    exit_price = position['stop_loss'] * (1 - self.slippage)
                    pnl = (exit_price - position['entry_price']) * position['shares']
                    pnl -= position['shares'] * exit_price * self.commission

                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'shares': position['shares'],
                        'pnl': pnl,
                        'return_pct': (exit_price - position['entry_price']) / position['entry_price'],
                        'exit_reason': 'stop_loss'
                    })

                    capital += position['shares'] * exit_price + pnl
                    positions.remove(position)

                    logger.info(f"STOP-LOSS: {current_date.date()} ${exit_price:.2f} P/L=${pnl:.2f}")

                # Target kontrolü
                elif current_price >= position['target']:
                    # Hedefe ulaşıldı
                    exit_price = position['target'] * (1 - self.slippage)
                    pnl = (exit_price - position['entry_price']) * position['shares']
                    pnl -= position['shares'] * exit_price * self.commission

                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'shares': position['shares'],
                        'pnl': pnl,
                        'return_pct': (exit_price - position['entry_price']) / position['entry_price'],
                        'exit_reason': 'target'
                    })

                    capital += position['shares'] * exit_price + pnl
                    positions.remove(position)

                    logger.info(f"TARGET HIT: {current_date.date()} ${exit_price:.2f} P/L=${pnl:.2f}")

            # YENİ POZİSYON AÇMA KONTROLÜ
            if len(positions) == 0 and capital > 0:
                # Sinyal kontrolü
                if self._check_buy_signal(tech, levels, current_price):
                    # Al sinyali
                    strategy = self.pm.create_entry_strategy(
                        support_levels=levels['support'],
                        resistance_levels=levels['resistance'],
                        current_price=current_price,
                        atr=tech['atr']['value']
                    )

                    # Pozisyon boyutu
                    if strategy['risk_reward_ratio'] >= 1.5:
                        entry_price = current_price * (1 + self.slippage)
                        size = self.pm.calculate_position_size(
                            capital=capital * 0.3,  # Sermayenin %30'u
                            entry_price=entry_price,
                            stop_loss=strategy['stop_loss']
                        )

                        if size['shares'] > 0:
                            cost = size['position_value'] * (1 + self.commission)

                            if cost <= capital:
                                positions.append({
                                    'entry_date': current_date,
                                    'entry_price': entry_price,
                                    'shares': size['shares'],
                                    'stop_loss': strategy['stop_loss'],
                                    'target': strategy['target'],
                                })

                                capital -= cost

                                logger.info(
                                    f"BUY: {current_date.date()} "
                                    f"${entry_price:.2f} x {size['shares']:.2f} shares"
                                )

            # Equity curve güncelle
            total_value = capital
            for pos in positions:
                total_value += pos['shares'] * current_price

            equity_curve.append(total_value)
            dates.append(current_date)

        # Kalan pozisyonları kapat (backtest sonu)
        final_price = float(data['Close'].iloc[-1])
        for position in positions:
            exit_price = final_price * (1 - self.slippage)
            pnl = (exit_price - position['entry_price']) * position['shares']

            trades.append({
                'entry_date': position['entry_date'],
                'exit_date': data.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'shares': position['shares'],
                'pnl': pnl,
                'return_pct': (exit_price - position['entry_price']) / position['entry_price'],
                'exit_reason': 'backtest_end'
            })

            capital += position['shares'] * exit_price

        # Sonuçları hesapla
        results = self._calculate_results(trades, equity_curve, dates)

        logger.info(
            f"Backtest tamamlandı: {len(trades)} işlem, "
            f"Final sermaye=${results['final_capital']:.2f}"
        )

        return results

    def _check_buy_signal(
            self,
            tech: Dict,
            levels: Dict,
            current_price: float
    ) -> bool:
        """
        Alım sinyali kontrolü

        Args:
            tech: Teknik analiz
            levels: S/R seviyeleri
            current_price: Mevcut fiyat

        Returns:
            bool: Al sinyali var mı
        """
        # Destek yakınında mı
        if not levels['support']:
            return False

        nearest_support = levels['support'][0]
        distance_to_support = (current_price - nearest_support) / current_price

        # RSI aşırı satımda mı
        rsi_oversold = tech['rsi']['status'] == 'oversold'

        # MACD pozitif mi
        macd_positive = tech['macd']['status'] == 'bullish'

        # Sinyal: Destekte + (RSI oversold VEYA MACD bullish)
        signal = (distance_to_support < 0.02) and (rsi_oversold or macd_positive)

        return signal

    def _calculate_results(
            self,
            trades: List[Dict],
            equity_curve: List[float],
            dates: List
    ) -> Dict[str, any]:
        """
        Backtest sonuçlarını hesapla
        """
        if not trades:
            return {
                'total_trades': 0,
                'final_capital': self.initial_capital,
                'total_return_pct': 0,
                'error': 'Hiç işlem yapılmadı'
            }

        trades_df = pd.DataFrame(trades)

        # Kazançlar
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        results = {
            'initial_capital': self.initial_capital,
            'final_capital': equity_curve[-1],
            'total_return': equity_curve[-1] - self.initial_capital,
            'total_return_pct': ((equity_curve[-1] - self.initial_capital) / self.initial_capital) * 100,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades) if len(trades) > 0 else 0,
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            'largest_win': trades_df['pnl'].max(),
            'largest_loss': trades_df['pnl'].min(),
            'equity_curve': equity_curve,
            'dates': dates,
            'trades': trades,
        }

        return results