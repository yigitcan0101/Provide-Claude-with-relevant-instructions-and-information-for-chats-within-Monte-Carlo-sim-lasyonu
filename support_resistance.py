"""
Destek ve Direnç seviyesi tespit modülü
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.signal import argrelextrema

from utils.logger import logger


class SupportResistance:
    """
    Destek ve Direnç seviyelerini otomatik tespit eden sınıf
    """

    def __init__(self):
        """
        SupportResistance başlatıcı
        """
        logger.info("SupportResistance başlatıldı")

    def find_support_resistance_levels(
            self,
            data: pd.DataFrame,
            order: int = 5,
            num_levels: int = 3
    ) -> Dict[str, List[float]]:
        """
        Destek ve direnç seviyelerini tespit et

        Args:
            data: Fiyat verisi
            order: Lokal min/max için komşuluk (varsayılan: 5)
            num_levels: Döndürülecek seviye sayısı (varsayılan: 3)

        Returns:
            dict: {'support': [s1, s2, s3], 'resistance': [r1, r2, r3]}
        """
        # Multi-index düzleştir
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values

        # Lokal minimumlar (destek seviyeleri)
        local_min_indices = argrelextrema(lows, np.less_equal, order=order)[0]
        support_levels = lows[local_min_indices]

        # Lokal maksimumlar (direnç seviyeleri)
        local_max_indices = argrelextrema(highs, np.greater_equal, order=order)[0]
        resistance_levels = highs[local_max_indices]

        # Seviyeleri grupla (birbirine yakın olanları birleştir)
        support_levels = self._cluster_levels(support_levels, tolerance=0.02)
        resistance_levels = self._cluster_levels(resistance_levels, tolerance=0.02)

        # Mevcut fiyata göre filtrele
        current_price = float(closes[-1])

        # Destek: Mevcut fiyatın altındaki seviyeler
        support_below = [s for s in support_levels if s < current_price]
        support_below = sorted(support_below, reverse=True)[:num_levels]

        # Direnç: Mevcut fiyatın üstündeki seviyeler
        resistance_above = [r for r in resistance_levels if r > current_price]
        resistance_above = sorted(resistance_above)[:num_levels]

        # Eğer yeterli seviye yoksa, yakın geçmişten ekle
        if len(support_below) < num_levels:
            recent_lows = sorted(lows[-252:])[:num_levels]  # Son 1 yıl
            for low in recent_lows:
                if low < current_price and low not in support_below:
                    support_below.append(low)
                if len(support_below) >= num_levels:
                    break

        if len(resistance_above) < num_levels:
            recent_highs = sorted(highs[-252:], reverse=True)[:num_levels]
            for high in recent_highs:
                if high > current_price and high not in resistance_above:
                    resistance_above.append(high)
                if len(resistance_above) >= num_levels:
                    break

        results = {
            'support': [float(s) for s in sorted(support_below, reverse=True)[:num_levels]],
            'resistance': [float(r) for r in sorted(resistance_above)[:num_levels]],
            'current_price': current_price,
        }

        logger.info(
            f"Destek/Direnç tespit edildi: "
            f"{len(results['support'])} destek, {len(results['resistance'])} direnç"
        )

        return results

    def _cluster_levels(
            self,
            levels: np.ndarray,
            tolerance: float = 0.02
    ) -> List[float]:
        """
        Birbirine yakın seviyeleri birleştir

        Args:
            levels: Seviye listesi
            tolerance: Birleştirme toleransı (varsayılan: %2)

        Returns:
            list: Kümelenmiş seviyeler
        """
        if len(levels) == 0:
            return []

        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]

        for level in levels[1:]:
            # Mevcut kümenin ortalamasına göre kontrol et
            cluster_mean = np.mean(current_cluster)

            if abs(level - cluster_mean) / cluster_mean <= tolerance:
                # Aynı kümeye ekle
                current_cluster.append(level)
            else:
                # Yeni küme başlat
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]

        # Son kümeyi ekle
        clustered.append(np.mean(current_cluster))

        return clustered

    def calculate_strength(
            self,
            data: pd.DataFrame,
            level: float,
            level_type: str = 'support',
            tolerance: float = 0.01
    ) -> int:
        """
        Seviye gücünü hesapla (kaç kez test edildi)

        Args:
            data: Fiyat verisi
            level: Seviye fiyatı
            level_type: 'support' veya 'resistance'
            tolerance: Seviye toleransı (varsayılan: %1)

        Returns:
            int: Test sayısı (güç)
        """
        # Multi-index düzleştir
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        touches = 0

        if level_type == 'support':
            # Low değerlerinin seviyeye yaklaştığı noktalar
            lows = data['Low'].values
            for low in lows:
                if abs(low - level) / level <= tolerance:
                    touches += 1

        elif level_type == 'resistance':
            # High değerlerinin seviyeye yaklaştığı noktalar
            highs = data['High'].values
            for high in highs:
                if abs(high - level) / level <= tolerance:
                    touches += 1

        return touches

    def find_nearest_support_resistance(
            self,
            data: pd.DataFrame
    ) -> Dict[str, float]:
        """
        En yakın destek ve direnç seviyelerini bul

        Args:
            data: Fiyat verisi

        Returns:
            dict: En yakın destek ve direnç
        """
        levels = self.find_support_resistance_levels(data)

        current_price = levels['current_price']
        supports = levels['support']
        resistances = levels['resistance']

        nearest_support = supports[0] if supports else None
        nearest_resistance = resistances[0] if resistances else None

        result = {
            'current_price': current_price,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
        }

        if nearest_support:
            result['support_distance'] = (current_price - nearest_support) / current_price
            result['support_distance_pct'] = result['support_distance'] * 100

        if nearest_resistance:
            result['resistance_distance'] = (nearest_resistance - current_price) / current_price
            result['resistance_distance_pct'] = result['resistance_distance'] * 100

        logger.info(
            f"En yakın seviyeler: "
            f"Destek=${nearest_support:.2f}, Direnç=${nearest_resistance:.2f}"
        )

        return result

    def get_key_levels_with_strength(
            self,
            data: pd.DataFrame,
            num_levels: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Güç değerleri ile birlikte anahtar seviyeleri getir

        Args:
            data: Fiyat verisi
            num_levels: Seviye sayısı

        Returns:
            dict: Güç değerleri ile seviyeler
        """
        levels = self.find_support_resistance_levels(data, num_levels=num_levels)

        # Destek seviyeleri için güç hesapla
        support_with_strength = []
        for level in levels['support']:
            strength = self.calculate_strength(data, level, 'support')
            support_with_strength.append({
                'price': level,
                'strength': strength,
                'type': 'support'
            })

        # Direnç seviyeleri için güç hesapla
        resistance_with_strength = []
        for level in levels['resistance']:
            strength = self.calculate_strength(data, level, 'resistance')
            resistance_with_strength.append({
                'price': level,
                'strength': strength,
                'type': 'resistance'
            })

        results = {
            'support_levels': support_with_strength,
            'resistance_levels': resistance_with_strength,
            'current_price': levels['current_price'],
        }

        logger.info("Güç değerleri ile seviyeler hesaplandı")
        return results

    def is_at_support(
            self,
            data: pd.DataFrame,
            tolerance: float = 0.02
    ) -> bool:
        """
        Fiyat destek seviyesinde mi kontrol et

        Args:
            data: Fiyat verisi
            tolerance: Tolerans (varsayılan: %2)

        Returns:
            bool: Destek seviyesinde ise True
        """
        nearest = self.find_nearest_support_resistance(data)

        if nearest['nearest_support'] is None:
            return False

        distance_pct = nearest['support_distance_pct']

        return distance_pct <= (tolerance * 100)

    def is_at_resistance(
            self,
            data: pd.DataFrame,
            tolerance: float = 0.02
    ) -> bool:
        """
        Fiyat direnç seviyesinde mi kontrol et

        Args:
            data: Fiyat verisi
            tolerance: Tolerans (varsayılan: %2)

        Returns:
            bool: Direnç seviyesinde ise True
        """
        nearest = self.find_nearest_support_resistance(data)

        if nearest['nearest_resistance'] is None:
            return False

        distance_pct = nearest['resistance_distance_pct']

        return distance_pct <= (tolerance * 100)

    def get_breakout_potential(
            self,
            data: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Kırılım potansiyeli analizi

        Args:
            data: Fiyat verisi

        Returns:
            dict: Kırılım potansiyeli bilgisi
        """
        # Multi-index düzleştir
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        nearest = self.find_nearest_support_resistance(data)
        current_price = nearest['current_price']

        # Son 20 günün volatilitesi
        recent_volatility = data['Close'].tail(20).pct_change().std()

        # Dirence olan mesafe
        if nearest['nearest_resistance']:
            resistance_distance = nearest['resistance_distance_pct']
            resistance_strength = self.calculate_strength(
                data,
                nearest['nearest_resistance'],
                'resistance'
            )

            # Kırılım potansiyeli
            # Düşük mesafe + düşük direnç gücü = yüksek potansiyel
            if resistance_distance < 3 and resistance_strength < 3:
                resistance_breakout_potential = "Yüksek"
            elif resistance_distance < 5 and resistance_strength < 5:
                resistance_breakout_potential = "Orta"
            else:
                resistance_breakout_potential = "Düşük"
        else:
            resistance_distance = None
            resistance_strength = None
            resistance_breakout_potential = "Bilinmiyor"

        # Destekten olan mesafe
        if nearest['nearest_support']:
            support_distance = nearest['support_distance_pct']
            support_strength = self.calculate_strength(
                data,
                nearest['nearest_support'],
                'support'
            )

            # Kırılım riski
            if support_distance < 3 and support_strength < 3:
                support_breakdown_risk = "Yüksek"
            elif support_distance < 5 and support_strength < 5:
                support_breakdown_risk = "Orta"
            else:
                support_breakdown_risk = "Düşük"
        else:
            support_distance = None
            support_strength = None
            support_breakdown_risk = "Bilinmiyor"

        results = {
            'current_price': current_price,
            'volatility': float(recent_volatility),
            'resistance': {
                'price': nearest['nearest_resistance'],
                'distance_pct': resistance_distance,
                'strength': resistance_strength,
                'breakout_potential': resistance_breakout_potential,
            },
            'support': {
                'price': nearest['nearest_support'],
                'distance_pct': support_distance,
                'strength': support_strength,
                'breakdown_risk': support_breakdown_risk,
            }
        }

        logger.info("Kırılım potansiyeli analiz edildi")
        return results