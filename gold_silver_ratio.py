"""
Gold-Silver Ratio analizi
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional

from utils.logger import logger
from config.asset_config import GOLD_SILVER_RATIO


class GoldSilverRatio:
    """
    XAU/XAG ratio analizi
    """

    def __init__(self):
        """
        GoldSilverRatio başlatıcı
        """
        self.historical_avg = GOLD_SILVER_RATIO['historical_avg']
        self.high_threshold = GOLD_SILVER_RATIO['high_threshold']
        self.low_threshold = GOLD_SILVER_RATIO['low_threshold']

        logger.info("GoldSilverRatio başlatıldı")

    def calculate_ratio(
            self,
            gold_price: float,
            silver_price: float
    ) -> float:
        """
        Altın/Gümüş oranını hesapla

        Args:
            gold_price: Altın fiyatı ($/oz)
            silver_price: Gümüş fiyatı ($/oz)

        Returns:
            float: Ratio
        """
        if silver_price == 0:
            logger.error("Silver price sıfır!")
            return 0.0

        ratio = gold_price / silver_price

        logger.info(f"Gold/Silver Ratio: {ratio:.2f}")
        return float(ratio)

    def analyze_ratio(
            self,
            gold_data: pd.DataFrame,
            silver_data: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Ratio analizi

        Args:
            gold_data: Altın fiyat verisi
            silver_data: Gümüş fiyat verisi

        Returns:
            dict: Ratio analizi
        """
        # Multi-index düzleştir
        if isinstance(gold_data.columns, pd.MultiIndex):
            gold_data.columns = gold_data.columns.get_level_values(0)
        if isinstance(silver_data.columns, pd.MultiIndex):
            silver_data.columns = silver_data.columns.get_level_values(0)

        # Tarihleri hizala
        merged = pd.merge(
            gold_data[['Close']],
            silver_data[['Close']],
            left_index=True,
            right_index=True,
            suffixes=('_gold', '_silver')
        )

        # Ratio hesapla
        merged['Ratio'] = merged['Close_gold'] / merged['Close_silver']

        current_ratio = float(merged['Ratio'].iloc[-1])
        avg_ratio = float(merged['Ratio'].mean())
        std_ratio = float(merged['Ratio'].std())
        min_ratio = float(merged['Ratio'].min())
        max_ratio = float(merged['Ratio'].max())

        # Değerlendirme
        if current_ratio > self.high_threshold:
            signal = "Gümüş Ucuz (AL)"
            interpretation = f"Ratio {self.high_threshold}'in üstünde. Gümüş altına göre ucuz."
        elif current_ratio < self.low_threshold:
            signal = "Altın Ucuz (AL)"
            interpretation = f"Ratio {self.low_threshold}'in altında. Altın gümüşe göre ucuz."
        else:
            signal = "Normal Seviyelerde"
            interpretation = "Ratio normal aralıkta."

        # Z-score (kaç standart sapma)
        z_score = (current_ratio - avg_ratio) / std_ratio

        result = {
            'current_ratio': current_ratio,
            'current_gold_price': float(merged['Close_gold'].iloc[-1]),
            'current_silver_price': float(merged['Close_silver'].iloc[-1]),
            'historical_average': self.historical_avg,
            'period_average': avg_ratio,
            'std_dev': std_ratio,
            'min_ratio': min_ratio,
            'max_ratio': max_ratio,
            'z_score': float(z_score),
            'signal': signal,
            'interpretation': interpretation,
            'thresholds': {
                'high': self.high_threshold,
                'low': self.low_threshold,
            }
        }

        logger.info(
            f"Ratio analizi: {current_ratio:.2f} "
            f"(Ortalama: {avg_ratio:.2f}, Sinyal: {signal})"
        )

        return result

    def ratio_trading_signal(
            self,
            gold_data: pd.DataFrame,
            silver_data: pd.DataFrame
    ) -> Dict[str, str]:
        """
        Ratio bazlı trading sinyali

        Args:
            gold_data: Altın verisi
            silver_data: Gümüş verisi

        Returns:
            dict: Trading sinyali
        """
        analysis = self.analyze_ratio(gold_data, silver_data)

        ratio = analysis['current_ratio']
        z_score = analysis['z_score']

        # Sinyal üretme
        if ratio > self.high_threshold and z_score > 1:
            # Gümüş aşırı ucuz
            gold_action = "SAT"
            silver_action = "AL"
            strategy = "PAIR TRADE: Altın sat, Gümüş al"
            confidence = "Yüksek" if z_score > 2 else "Orta"

        elif ratio < self.low_threshold and z_score < -1:
            # Altın aşırı ucuz
            gold_action = "AL"
            silver_action = "SAT"
            strategy = "PAIR TRADE: Altın al, Gümüş sat"
            confidence = "Yüksek" if z_score < -2 else "Orta"

        else:
            gold_action = "BEKLE"
            silver_action = "BEKLE"
            strategy = "İşlem yok (Ratio normal)"
            confidence = "Düşük"

        signal = {
            'gold_action': gold_action,
            'silver_action': silver_action,
            'strategy': strategy,
            'confidence': confidence,
            'ratio': ratio,
            'z_score': z_score,
        }

        logger.info(f"Trading sinyali: {strategy} (Confidence: {confidence})")
        return signal