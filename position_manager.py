"""
Pozisyon yönetimi ve kademeli alım stratejisi
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

from utils.logger import logger
from config.settings import STRATEGY_CONFIG


class PositionManager:
    """
    3 kademeli alım stratejisi ve pozisyon yönetimi
    """

    def __init__(self):
        """
        PositionManager başlatıcı
        """
        self.entry_levels = STRATEGY_CONFIG['entry_levels']
        self.stop_loss_multiplier = STRATEGY_CONFIG['stop_loss_multiplier']
        self.risk_per_trade = STRATEGY_CONFIG['risk_per_trade']
        self.min_risk_reward = STRATEGY_CONFIG['min_risk_reward']

        logger.info("PositionManager başlatıldı")

    def create_entry_strategy(
            self,
            support_levels: List[float],
            resistance_levels: List[float],
            current_price: float,
            atr: float
    ) -> Dict[str, any]:
        """
        3 kademeli giriş stratejisi oluştur

        Args:
            support_levels: Destek seviyeleri
            resistance_levels: Direnç seviyeleri
            current_price: Mevcut fiyat
            atr: ATR değeri

        Returns:
            dict: Giriş stratejisi
        """
        # En yakın destek ve direnç
        nearest_support = support_levels[0] if support_levels else current_price * 0.95
        nearest_resistance = resistance_levels[0] if resistance_levels else current_price * 1.10

        # Stop-loss: En yakın desteğin altında (ATR bazlı)
        stop_loss = nearest_support - (atr * self.stop_loss_multiplier)

        # Target: En yakın direnç (konservatif)
        target_price = nearest_resistance

        # Risk/Reward hesapla
        risk = current_price - stop_loss
        reward = target_price - current_price
        risk_reward_ratio = reward / risk if risk > 0 else 0

        # 3 Kademeli Giriş Noktaları
        # Kademe 1: Mevcut fiyattan (hemen giriş)
        entry_1 = current_price

        # Kademe 2: Destek seviyesine yakın (daha iyi fiyat)
        if current_price > nearest_support:
            entry_2 = nearest_support + (atr * 0.5)
        else:
            entry_2 = current_price * 0.98

        # Kademe 3: Güçlü destek (en düşük risk)
        if len(support_levels) > 1:
            entry_3 = support_levels[1]
        else:
            entry_3 = nearest_support * 0.97

        # Her kademede pozisyon boyutu (toplam %100)
        position_sizes = self._calculate_position_distribution()

        strategy = {
            'current_price': current_price,
            'entries': [
                {
                    'level': 1,
                    'price': float(entry_1),
                    'size_pct': position_sizes[0],
                    'description': 'Hemen Giriş (Momentum)'
                },
                {
                    'level': 2,
                    'price': float(entry_2),
                    'size_pct': position_sizes[1],
                    'description': 'Destek Yakını (Orta Risk)'
                },
                {
                    'level': 3,
                    'price': float(entry_3),
                    'size_pct': position_sizes[2],
                    'description': 'Güçlü Destek (Düşük Risk)'
                }
            ],
            'stop_loss': float(stop_loss),
            'target': float(target_price),
            'risk_reward_ratio': float(risk_reward_ratio),
            'atr_used': float(atr),
            'nearest_support': float(nearest_support),
            'nearest_resistance': float(nearest_resistance),
        }

        # Risk/Reward kontrolü
        if risk_reward_ratio < self.min_risk_reward:
            strategy['warning'] = f"Düşük R:R oranı ({risk_reward_ratio:.2f}). Minimum {self.min_risk_reward} önerilir."
            logger.warning(f"Düşük R:R oranı: {risk_reward_ratio:.2f}")
        else:
            strategy['warning'] = None
            logger.info(f"✅ İyi R:R oranı: {risk_reward_ratio:.2f}")

        logger.info(
            f"3 kademeli strateji oluşturuldu: "
            f"Giriş=[${entry_1:.2f}, ${entry_2:.2f}, ${entry_3:.2f}], "
            f"Stop=${stop_loss:.2f}, Target=${target_price:.2f}"
        )

        return strategy

    def _calculate_position_distribution(self) -> List[float]:
        """
        Pozisyon dağılımını hesapla

        Returns:
            list: [%40, %35, %25] gibi yüzdeler
        """
        # Konservatif yaklaşım: İlk girişte az, desteklerde daha fazla
        distributions = [
            [33.33, 33.33, 33.34],  # Eşit dağılım
            [40, 35, 25],  # İlk girişte biraz fazla
            [30, 35, 35],  # Desteklerde daha ağırlıklı
            [25, 35, 40],  # En konservatif (en düşükte en fazla)
        ]

        # Varsayılan: Orta yol (index 2)
        return distributions[2]

    def calculate_position_size(
            self,
            capital: float,
            entry_price: float,
            stop_loss: float,
            risk_pct: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Pozisyon büyüklüğünü hesapla (risk bazlı)

        Args:
            capital: Toplam sermaye
            entry_price: Giriş fiyatı
            stop_loss: Stop-loss fiyatı
            risk_pct: Risk yüzdesi (varsayılan: config'den)

        Returns:
            dict: Pozisyon detayları
        """
        risk_pct = risk_pct or self.risk_per_trade

        # Risk miktarı (sermayenin %2'si)
        risk_amount = capital * risk_pct

        # Hisse başına risk
        risk_per_share = entry_price - stop_loss

        if risk_per_share <= 0:
            logger.error("Geçersiz stop-loss! Stop, giriş fiyatının altında olmalı.")
            return {
                'shares': 0,
                'position_value': 0,
                'risk_amount': 0,
                'error': 'Invalid stop-loss'
            }

        # Kaç hisse alınacak
        shares = risk_amount / risk_per_share

        # Pozisyon değeri
        position_value = shares * entry_price

        result = {
            'shares': float(shares),
            'position_value': float(position_value),
            'risk_amount': float(risk_amount),
            'risk_per_share': float(risk_per_share),
            'capital_used_pct': float(position_value / capital * 100),
        }

        logger.info(
            f"Pozisyon hesaplandı: {shares:.2f} hisse, "
            f"Değer=${position_value:.2f} (Sermayenin %{result['capital_used_pct']:.1f}'si)"
        )

        return result

    def trailing_stop_loss(
            self,
            entry_price: float,
            current_price: float,
            initial_stop: float,
            atr: float,
            trailing_multiplier: float = 2.0
    ) -> float:
        """
        Trailing stop-loss hesapla (fiyat yükseldikçe stop'u yukarı çek)

        Args:
            entry_price: Giriş fiyatı
            current_price: Mevcut fiyat
            initial_stop: İlk stop-loss
            atr: ATR değeri
            trailing_multiplier: ATR çarpanı

        Returns:
            float: Yeni stop-loss seviyesi
        """
        # Kar varsa trailing stop kullan
        if current_price > entry_price:
            # Stop'u mevcut fiyatın ATR x multiplier altına çek
            new_stop = current_price - (atr * trailing_multiplier)

            # Eski stop'tan yüksekse güncelle
            new_stop = max(new_stop, initial_stop)

            logger.info(f"Trailing stop güncellendi: ${initial_stop:.2f} → ${new_stop:.2f}")
            return float(new_stop)
        else:
            # Henüz kar yok, ilk stop'u koru
            return float(initial_stop)

    def partial_exit_strategy(
            self,
            entry_price: float,
            current_price: float,
            target_price: float,
            total_shares: float
    ) -> Dict[str, any]:
        """
        Kısmi çıkış stratejisi (kademeli kar realizasyonu)

        Args:
            entry_price: Giriş fiyatı
            current_price: Mevcut fiyat
            target_price: Hedef fiyat
            total_shares: Toplam hisse

        Returns:
            dict: Çıkış stratejisi
        """
        # Kâr yüzdesi
        profit_pct = (current_price - entry_price) / entry_price

        exits = []

        # %50 hedefe ulaşıldığında: %30 sat
        target_50_pct = entry_price + ((target_price - entry_price) * 0.5)
        if current_price >= target_50_pct:
            exits.append({
                'level': '50% Hedef',
                'price': target_50_pct,
                'shares': total_shares * 0.30,
                'reason': 'İlk kar realizasyonu'
            })

        # %75 hedefe ulaşıldığında: %30 daha sat
        target_75_pct = entry_price + ((target_price - entry_price) * 0.75)
        if current_price >= target_75_pct:
            exits.append({
                'level': '75% Hedef',
                'price': target_75_pct,
                'shares': total_shares * 0.30,
                'reason': 'İkinci kar realizasyonu'
            })

        # %100 hedefe ulaşıldığında: Kalan %40'ı sat
        if current_price >= target_price:
            exits.append({
                'level': '100% Hedef',
                'price': target_price,
                'shares': total_shares * 0.40,
                'reason': 'Hedef tamamlandı'
            })

        strategy = {
            'current_price': float(current_price),
            'profit_pct': float(profit_pct * 100),
            'exits': exits,
            'remaining_shares': float(total_shares - sum(e['shares'] for e in exits)),
        }

        if exits:
            logger.info(f"Kısmi çıkış stratejisi: {len(exits)} seviye aktif")

        return strategy

    def rebalance_position(
            self,
            current_positions: List[Dict],
            target_allocation: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Pozisyonları yeniden dengele

        Args:
            current_positions: Mevcut pozisyonlar
            target_allocation: Hedef dağılım (asset: %)

        Returns:
            dict: Yeniden dengeleme önerileri
        """
        total_value = sum(p['value'] for p in current_positions)

        rebalancing = []

        for position in current_positions:
            asset = position['asset']
            current_value = position['value']
            current_pct = (current_value / total_value) * 100

            target_pct = target_allocation.get(asset, 0)
            target_value = total_value * (target_pct / 100)

            diff = target_value - current_value
            diff_pct = diff / current_value * 100 if current_value > 0 else 0

            if abs(diff_pct) > 5:  # %5'ten fazla sapma varsa
                action = 'Al' if diff > 0 else 'Sat'
                rebalancing.append({
                    'asset': asset,
                    'current_pct': current_pct,
                    'target_pct': target_pct,
                    'action': action,
                    'amount': abs(diff),
                })

        result = {
            'total_portfolio_value': total_value,
            'rebalancing_needed': len(rebalancing) > 0,
            'actions': rebalancing,
        }

        if rebalancing:
            logger.info(f"Yeniden dengeleme gerekli: {len(rebalancing)} asset")
        else:
            logger.info("Portföy dengede, işlem gerekmiyor")

        return result