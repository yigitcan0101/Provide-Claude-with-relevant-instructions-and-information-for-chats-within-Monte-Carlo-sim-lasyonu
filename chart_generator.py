"""
Grafik oluşturucu (Matplotlib)
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path

from utils.logger import logger
from config.settings import OUTPUT_CONFIG


class ChartGenerator:
    """
    Analiz grafikleri oluşturur
    """

    def __init__(self):
        """
        ChartGenerator başlatıcı
        """
        self.charts_dir = OUTPUT_CONFIG['charts_dir']
        self.dpi = OUTPUT_CONFIG['chart_dpi']
        self.size = OUTPUT_CONFIG['chart_size']

        # Klasör oluştur
        self.charts_dir.mkdir(parents=True, exist_ok=True)

        logger.info("ChartGenerator başlatıldı")

    def create_price_chart(
            self,
            data: pd.DataFrame,
            technical_indicators: Dict,
            filename: str = 'price_chart.png'
    ) -> str:
        """
        Fiyat + Teknik göstergeler grafiği

        Args:
            data: Fiyat verisi (göstergeler dahil)
            technical_indicators: Teknik analiz sonuçları
            filename: Dosya adı

        Returns:
            str: Dosya yolu
        """
        fig, axes = plt.subplots(3, 1, figsize=self.size, height_ratios=[3, 1, 1])

        # Alt grafik 1: Fiyat + EMA + Bollinger Bands
        ax1 = axes[0]
        ax1.plot(data.index, data['Close'], label='Close', color='black', linewidth=1.5)

        if 'EMA20' in data.columns:
            ax1.plot(data.index, data['EMA20'], label='EMA20', alpha=0.7)
            ax1.plot(data.index, data['EMA50'], label='EMA50', alpha=0.7)
            ax1.plot(data.index, data['EMA200'], label='EMA200', alpha=0.7)

        if 'BB_High' in data.columns:
            ax1.fill_between(
                data.index,
                data['BB_Low'],
                data['BB_High'],
                alpha=0.1,
                color='gray',
                label='Bollinger Bands'
            )

        # Destek/Direnç çizgileri
        if 'support_levels' in technical_indicators:
            for support in technical_indicators['support_levels'][:3]:
                ax1.axhline(y=support['price'], color='green', linestyle='--', alpha=0.5)

        if 'resistance_levels' in technical_indicators:
            for resistance in technical_indicators['resistance_levels'][:3]:
                ax1.axhline(y=resistance['price'], color='red', linestyle='--', alpha=0.5)

        ax1.set_ylabel('Fiyat ($)')
        ax1.legend(loc='upper left')
        ax1.grid(alpha=0.3)
        ax1.set_title('Fiyat Hareketi ve Teknik Göstergeler', fontsize=14, fontweight='bold')

        # Alt grafik 2: RSI
        ax2 = axes[1]
        if 'RSI' in data.columns:
            ax2.plot(data.index, data['RSI'], label='RSI', color='purple')
            ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Aşırı Alım')
            ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Aşırı Satım')
            ax2.fill_between(data.index, 30, 70, alpha=0.1, color='gray')

        ax2.set_ylabel('RSI')
        ax2.set_ylim(0, 100)
        ax2.legend(loc='upper left')
        ax2.grid(alpha=0.3)

        # Alt grafik 3: MACD
        ax3 = axes[2]
        if 'MACD' in data.columns:
            ax3.plot(data.index, data['MACD'], label='MACD', color='blue')
            ax3.plot(data.index, data['MACD_Signal'], label='Signal', color='red')
            ax3.bar(data.index, data['MACD_Diff'], label='Histogram', alpha=0.3)

        ax3.set_ylabel('MACD')
        ax3.legend(loc='upper left')
        ax3.grid(alpha=0.3)
        ax3.set_xlabel('Tarih')

        plt.tight_layout()

        filepath = self.charts_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Fiyat grafiği oluşturuldu: {filepath}")
        return str(filepath)

    def create_monte_carlo_chart(
            self,
            price_paths: np.ndarray,
            current_price: float,
            percentiles: Dict,
            filename: str = 'monte_carlo.png'
    ) -> str:
        """
        Monte Carlo simülasyon grafiği

        Args:
            price_paths: Simülasyon yolları
            current_price: Mevcut fiyat
            percentiles: Percentile değerleri
            filename: Dosya adı

        Returns:
            str: Dosya yolu
        """
        fig, ax = plt.subplots(figsize=self.size)

        # İlk 100 simülasyon yolunu çiz
        for i in range(min(100, price_paths.shape[0])):
            ax.plot(price_paths[i], alpha=0.1, color='blue', linewidth=0.5)

        # Medyan çizgisi
        median_path = np.median(price_paths, axis=0)
        ax.plot(median_path, color='red', linewidth=2, label='Medyan')

        # Percentile aralıkları
        p5 = np.percentile(price_paths, 5, axis=0)
        p95 = np.percentile(price_paths, 95, axis=0)

        ax.fill_between(
            range(len(p5)),
            p5,
            p95,
            alpha=0.2,
            color='green',
            label='%5-%95 Aralığı'
        )

        # Başlangıç fiyatı
        ax.axhline(y=current_price, color='black', linestyle='--', label=f'Mevcut: ${current_price:.2f}')

        ax.set_xlabel('Gün')
        ax.set_ylabel('Fiyat ($)')
        ax.set_title('Monte Carlo Simülasyonu (10,000 Senaryo)', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)

        filepath = self.charts_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Monte Carlo grafiği oluşturuldu: {filepath}")
        return str(filepath)

    def create_distribution_chart(
            self,
            final_prices: np.ndarray,
            current_price: float,
            filename: str = 'distribution.png'
    ) -> str:
        """
        Fiyat dağılım histogramı

        Args:
            final_prices: Final fiyatlar
            current_price: Mevcut fiyat
            filename: Dosya adı

        Returns:
            str: Dosya yolu
        """
        fig, ax = plt.subplots(figsize=self.size)

        ax.hist(final_prices, bins=50, alpha=0.7, color='blue', edgecolor='black')

        # Medyan
        median = np.median(final_prices)
        ax.axvline(x=median, color='red', linestyle='--', linewidth=2, label=f'Medyan: ${median:.2f}')

        # Mevcut fiyat
        ax.axvline(x=current_price, color='black', linestyle='--', linewidth=2, label=f'Mevcut: ${current_price:.2f}')

        # Percentile'lar
        p5 = np.percentile(final_prices, 5)
        p95 = np.percentile(final_prices, 95)
        ax.axvline(x=p5, color='green', linestyle=':', alpha=0.7, label=f'%5: ${p5:.2f}')
        ax.axvline(x=p95, color='green', linestyle=':', alpha=0.7, label=f'%95: ${p95:.2f}')

        ax.set_xlabel('Fiyat ($)')
        ax.set_ylabel('Frekans')
        ax.set_title('1 Yıl Sonrası Fiyat Dağılımı', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)

        filepath = self.charts_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Dağılım grafiği oluşturuldu: {filepath}")
        return str(filepath)

    def create_backtest_chart(
            self,
            equity_curve: List[float],
            dates: List,
            trades: List[Dict],
            filename: str = 'backtest.png'
    ) -> str:
        """
        Backtest equity curve grafiği

        Args:
            equity_curve: Sermaye eğrisi
            dates: Tarihler
            trades: İşlemler
            filename: Dosya adı

        Returns:
            str: Dosya yolu
        """
        fig, ax = plt.subplots(figsize=self.size)

        ax.plot(dates, equity_curve, linewidth=2, color='blue', label='Equity Curve')

        # İşlem noktaları
        for trade in trades:
            if trade['exit_reason'] == 'target':
                ax.scatter(trade['exit_date'], equity_curve[dates.index(trade['exit_date'])],
                          color='green', s=50, marker='^', alpha=0.7)
            elif trade['exit_reason'] == 'stop_loss':
                ax.scatter(trade['exit_date'], equity_curve[dates.index(trade['exit_date'])],
                          color='red', s=50, marker='v', alpha=0.7)

        ax.set_xlabel('Tarih')
        ax.set_ylabel('Sermaye ($)')
        ax.set_title('Backtest Sonuçları', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)

        filepath = self.charts_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Backtest grafiği oluşturuldu: {filepath}")
        return str(filepath)