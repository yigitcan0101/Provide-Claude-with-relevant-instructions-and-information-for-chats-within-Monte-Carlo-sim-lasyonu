"""
Teknik analiz motoru
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
import ta

from utils.logger import logger
from config.settings import TECHNICAL_CONFIG


class TechnicalAnalyzer:
    """
    Teknik analiz sınıfı - EMA, RSI, MACD, Fibonacci, Pivot Points
    """

    def __init__(self):
        """
        TechnicalAnalyzer başlatıcı
        """
        self.ema_periods = TECHNICAL_CONFIG['ema_periods']
        self.rsi_period = TECHNICAL_CONFIG['rsi_period']
        self.macd_fast = TECHNICAL_CONFIG['macd_fast']
        self.macd_slow = TECHNICAL_CONFIG['macd_slow']
        self.macd_signal = TECHNICAL_CONFIG['macd_signal']
        self.atr_period = TECHNICAL_CONFIG['atr_period']
        self.fibonacci_levels = TECHNICAL_CONFIG['fibonacci_levels']

        logger.info("TechnicalAnalyzer başlatıldı")

    def calculate_ema(
            self,
            data: pd.DataFrame,
            periods: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """
        Üssel Hareketli Ortalamalar (EMA) hesapla

        Args:
            data: Fiyat verisi
            periods: EMA periyotları (varsayılan: [20, 50, 200])

        Returns:
            pd.DataFrame: EMA kolonları eklenmiş veri
        """
        data = data.copy()
        periods = periods or self.ema_periods

        for period in periods:
            data[f'EMA{period}'] = ta.trend.ema_indicator(
                data['Close'],
                window=period
            )

        logger.info(f"EMA hesaplandı: {periods}")
        return data

    def calculate_rsi(
            self,
            data: pd.DataFrame,
            period: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Relative Strength Index (RSI) hesapla

        Args:
            data: Fiyat verisi
            period: RSI periyodu (varsayılan: 14)

        Returns:
            pd.DataFrame: RSI kolonu eklenmiş veri
        """
        data = data.copy()
        period = period or self.rsi_period

        data['RSI'] = ta.momentum.rsi(
            data['Close'],
            window=period
        )

        logger.info(f"RSI hesaplandı: period={period}")
        return data

    def calculate_macd(
            self,
            data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        MACD (Moving Average Convergence Divergence) hesapla

        Args:
            data: Fiyat verisi

        Returns:
            pd.DataFrame: MACD kolonları eklenmiş veri
        """
        data = data.copy()

        # MACD göstergesi
        macd_indicator = ta.trend.MACD(
            data['Close'],
            window_slow=self.macd_slow,
            window_fast=self.macd_fast,
            window_sign=self.macd_signal
        )

        data['MACD'] = macd_indicator.macd()
        data['MACD_Signal'] = macd_indicator.macd_signal()
        data['MACD_Diff'] = macd_indicator.macd_diff()

        logger.info(f"MACD hesaplandı: {self.macd_fast}-{self.macd_slow}-{self.macd_signal}")
        return data

    def calculate_atr(
            self,
            data: pd.DataFrame,
            period: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Average True Range (ATR) hesapla - volatilite ölçümü

        Args:
            data: Fiyat verisi (High, Low, Close olmalı)
            period: ATR periyodu (varsayılan: 14)

        Returns:
            pd.DataFrame: ATR kolonu eklenmiş veri
        """
        data = data.copy()
        period = period or self.atr_period

        data['ATR'] = ta.volatility.average_true_range(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            window=period
        )

        logger.info(f"ATR hesaplandı: period={period}")
        return data

    def fibonacci_retracement(
            self,
            high: float,
            low: float,
            levels: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """
        Fibonacci düzeltme seviyeleri hesapla

        Args:
            high: Tepe fiyat
            low: Dip fiyat
            levels: Fibonacci seviyeleri (varsayılan: [0.236, 0.382, 0.5, 0.618, 0.786])

        Returns:
            dict: Fibonacci seviyeleri
        """
        levels = levels or self.fibonacci_levels
        diff = high - low

        fib_levels = {
            'high': float(high),
            'low': float(low),
        }

        for level in levels:
            fib_levels[f'fib_{level}'] = float(high - (diff * level))

        logger.info(f"Fibonacci seviyeleri hesaplandı: {high:.2f} - {low:.2f}")
        return fib_levels

    def calculate_fibonacci_from_data(
            self,
            data: pd.DataFrame,
            lookback_days: int = 365
    ) -> Dict[str, float]:
        """
        Veri üzerinden Fibonacci seviyeleri hesapla

        Args:
            data: Fiyat verisi
            lookback_days: Geriye bakış günü (varsayılan: 1 yıl)

        Returns:
            dict: Fibonacci seviyeleri
        """
        # Son N günlük veriyi al
        recent_data = data.tail(lookback_days)

        high = float(recent_data['High'].max())
        low = float(recent_data['Low'].min())

        return self.fibonacci_retracement(high, low)

    def calculate_pivot_points(
            self,
            data: pd.DataFrame,
            years: int = 3
    ) -> Dict[str, float]:
        """
        Pivot Points hesapla (son N yıl)

        Args:
            data: Fiyat verisi
            years: Geriye bakış yılı (varsayılan: 3)

        Returns:
            dict: Pivot seviyeleri
        """
        # Son N yıllık veriyi al
        recent_data = data.tail(years * 252)  # 252 trading days/year

        high = float(recent_data['High'].max())
        low = float(recent_data['Low'].min())
        close = float(recent_data['Close'].iloc[-1])

        # Pivot Point (PP)
        pivot = (high + low + close) / 3

        # Destek ve Direnç seviyeleri
        resistance_1 = (2 * pivot) - low
        support_1 = (2 * pivot) - high

        resistance_2 = pivot + (high - low)
        support_2 = pivot - (high - low)

        resistance_3 = high + 2 * (pivot - low)
        support_3 = low - 2 * (high - pivot)

        pivots = {
            'pivot': float(pivot),
            'resistance_1': float(resistance_1),
            'resistance_2': float(resistance_2),
            'resistance_3': float(resistance_3),
            'support_1': float(support_1),
            'support_2': float(support_2),
            'support_3': float(support_3),
        }

        logger.info(f"Pivot Points hesaplandı: PP={pivot:.2f}")
        return pivots

    def detect_trend(
            self,
            data: pd.DataFrame,
            window: int = 50
    ) -> Dict[str, any]:
        """
        Trend tespiti (EMA bazlı)

        Args:
            data: Fiyat verisi (EMA'lar hesaplanmış olmalı)
            window: Trend tespiti için bakış penceresi

        Returns:
            dict: Trend bilgisi
        """
        # EMA'ları hesapla (yoksa)
        if 'EMA20' not in data.columns:
            data = self.calculate_ema(data)

        current_price = float(data['Close'].iloc[-1])
        ema20 = float(data['EMA20'].iloc[-1])
        ema50 = float(data['EMA50'].iloc[-1])
        ema200 = float(data['EMA200'].iloc[-1])

        # Trend belirleme
        if current_price > ema20 > ema50 > ema200:
            trend = "Güçlü Yükseliş"
            strength = "strong_bullish"
        elif current_price > ema20 > ema50:
            trend = "Yükseliş"
            strength = "bullish"
        elif current_price < ema20 < ema50 < ema200:
            trend = "Güçlü Düşüş"
            strength = "strong_bearish"
        elif current_price < ema20 < ema50:
            trend = "Düşüş"
            strength = "bearish"
        else:
            trend = "Yatay / Belirsiz"
            strength = "neutral"

        # Trend açısı (son N günlük EMA50 eğimi)
        ema50_slope = (ema50 - float(data['EMA50'].iloc[-window])) / window

        trend_info = {
            'trend': trend,
            'strength': strength,
            'current_price': current_price,
            'ema20': ema20,
            'ema50': ema50,
            'ema200': ema200,
            'ema50_slope': float(ema50_slope),
        }

        logger.info(f"Trend tespiti: {trend} ({strength})")
        return trend_info

    def calculate_bollinger_bands(
            self,
            data: pd.DataFrame,
            window: int = 20,
            std_dev: int = 2
    ) -> pd.DataFrame:
        """
        Bollinger Bands hesapla

        Args:
            data: Fiyat verisi
            window: MA penceresi (varsayılan: 20)
            std_dev: Standart sapma çarpanı (varsayılan: 2)

        Returns:
            pd.DataFrame: Bollinger Bands kolonları eklenmiş veri
        """
        data = data.copy()

        bb_indicator = ta.volatility.BollingerBands(
            data['Close'],
            window=window,
            window_dev=std_dev
        )

        data['BB_High'] = bb_indicator.bollinger_hband()
        data['BB_Mid'] = bb_indicator.bollinger_mavg()
        data['BB_Low'] = bb_indicator.bollinger_lband()
        data['BB_Width'] = bb_indicator.bollinger_wband()

        logger.info(f"Bollinger Bands hesaplandı: window={window}, std={std_dev}")
        return data

    def get_full_technical_analysis(
            self,
            data: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Tam teknik analiz (tüm göstergeler)

        Args:
            data: Fiyat verisi

        Returns:
            dict: Tüm teknik analiz sonuçları
        """
        logger.info("Tam teknik analiz başlıyor...")

        # Multi-index düzleştir
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Tüm göstergeleri hesapla
        data = self.calculate_ema(data)
        data = self.calculate_rsi(data)
        data = self.calculate_macd(data)
        data = self.calculate_atr(data)
        data = self.calculate_bollinger_bands(data)

        # Fibonacci seviyeleri
        fibonacci = self.calculate_fibonacci_from_data(data)

        # Pivot Points
        pivots = self.calculate_pivot_points(data)

        # Trend tespiti
        trend = self.detect_trend(data)

        # RSI değerlendirmesi
        current_rsi = float(data['RSI'].iloc[-1])
        if current_rsi > 70:
            rsi_signal = "Aşırı Alım (>70)"
            rsi_status = "overbought"
        elif current_rsi < 30:
            rsi_signal = "Aşırı Satım (<30)"
            rsi_status = "oversold"
        else:
            rsi_signal = "Normal (30-70)"
            rsi_status = "neutral"

        # MACD değerlendirmesi
        current_macd = float(data['MACD'].iloc[-1])
        current_signal = float(data['MACD_Signal'].iloc[-1])
        macd_diff = float(data['MACD_Diff'].iloc[-1])

        if current_macd > current_signal and macd_diff > 0:
            macd_signal = "Al Sinyali (MACD > Signal)"
            macd_status = "bullish"
        elif current_macd < current_signal and macd_diff < 0:
            macd_signal = "Sat Sinyali (MACD < Signal)"
            macd_status = "bearish"
        else:
            macd_signal = "Belirsiz"
            macd_status = "neutral"

        # Bollinger Bands pozisyonu
        current_price = float(data['Close'].iloc[-1])
        bb_high = float(data['BB_High'].iloc[-1])
        bb_low = float(data['BB_Low'].iloc[-1])
        bb_mid = float(data['BB_Mid'].iloc[-1])

        if current_price > bb_high:
            bb_position = "Üst Band Üzerinde (Aşırı Alım)"
        elif current_price < bb_low:
            bb_position = "Alt Band Altında (Aşırı Satım)"
        else:
            bb_position = "Bantlar Arasında"

        # Sonuçları birleştir
        results = {
            'current_price': current_price,
            'trend': trend,
            'rsi': {
                'value': current_rsi,
                'signal': rsi_signal,
                'status': rsi_status,
            },
            'macd': {
                'macd': current_macd,
                'signal': current_signal,
                'diff': macd_diff,
                'interpretation': macd_signal,
                'status': macd_status,
            },
            'ema': {
                'ema20': float(data['EMA20'].iloc[-1]),
                'ema50': float(data['EMA50'].iloc[-1]),
                'ema200': float(data['EMA200'].iloc[-1]),
            },
            'bollinger_bands': {
                'high': bb_high,
                'mid': bb_mid,
                'low': bb_low,
                'position': bb_position,
            },
            'fibonacci': fibonacci,
            'pivots': pivots,
            'atr': {
                'value': float(data['ATR'].iloc[-1]),
            },
            'data_with_indicators': data,
        }

        logger.info("Tam teknik analiz tamamlandı")
        return results