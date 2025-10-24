"""
Kullanıcı komutunu anlama ve parse etme
"""
import re
from typing import Dict, Optional, List
from datetime import datetime, timedelta

from utils.logger import logger


class CommandParser:
    """
    Doğal dil komutlarını parse eder
    """

    def __init__(self):
        """
        CommandParser başlatıcı
        """
        self.assets = ['silver', 'gold', 'gümüş', 'altın', 'xag', 'xau']
        self.analysis_types = [
            'monte carlo', 'teknik', 'analiz', 'strateji', 'backtest',
            'projeksiyon', 'tahmin', 'senaryo', 'destek', 'direnç'
        ]

        logger.info("CommandParser başlatıldı")

    def parse_command(self, command: str) -> Dict[str, any]:
        """
        Komutu parse et

        Args:
            command: Kullanıcı komutu

        Returns:
            dict: Parse edilmiş komut
        """
        command = command.lower().strip()

        result = {
            'original_command': command,
            'asset': self._extract_asset(command),
            'analysis_type': self._extract_analysis_type(command),
            'time_period': self._extract_time_period(command),
            'target_price': self._extract_target_price(command),
            'additional_params': {}
        }

        logger.info(f"Komut parse edildi: {result['asset']} - {result['analysis_type']}")
        return result

    def _extract_asset(self, command: str) -> str:
        """
        Asset'i çıkar (silver veya gold)
        """
        # Gümüş tespiti
        silver_keywords = ['gümüş', 'gumus', 'silver', 'xag', 'ag']
        for keyword in silver_keywords:
            if keyword in command:
                return 'silver'

        # Altın tespiti
        gold_keywords = ['altın', 'altin', 'gold', 'xau', 'au']
        for keyword in gold_keywords:
            if keyword in command:
                return 'gold'

        # Varsayılan: silver
        return 'silver'

    def _extract_analysis_type(self, command: str) -> str:
        """
        Analiz tipini çıkar
        """
        # TAM ANALİZ (ÖNCE BU KONTROL EDİLMELİ!)
        if 'tam analiz' in command or 'full analysis' in command or 'komple' in command:
            return 'full_analysis'

        # Monte Carlo
        if any(word in command for word in ['monte carlo', 'simülasyon', 'simulasyon', 'projeksiyon', 'tahmin']):
            return 'monte_carlo'

        # Teknik analiz
        if any(word in command for word in ['teknik', 'technical', 'gösterge', 'ema', 'rsi', 'macd']):
            return 'technical'

        # Destek/Direnç
        if any(word in command for word in ['destek', 'direnç', 'support', 'resistance', 'seviye']):
            return 'support_resistance'

        # Strateji
        if any(word in command for word in ['strateji öner', 'strategy', 'giriş noktası']):
            return 'strategy'

        # Backtest
        if any(word in command for word in ['backtest', 'test', 'geçmiş']):
            return 'backtest'

        # Varsayılan: tam analiz
        return 'full_analysis'

    def _extract_time_period(self, command: str) -> Optional[int]:
        """
        Zaman periyodunu çıkar (gün olarak döner)

        Returns:
            int: Gün sayısı veya None
        """
        import re

        # Yıl tespiti (4 yıl, 2 yıl, vb.)
        year_match = re.search(r'(\d+)\s*(?:yıl|yil|year|sene)', command)
        if year_match:
            years = int(year_match.group(1))
            return years * 252  # Trading günü

        # Ay tespiti (6 ay, 3 ay, vb.)
        month_match = re.search(r'(\d+)\s*(?:ay|month|mo)', command)
        if month_match:
            months = int(month_match.group(1))
            return months * 21  # Ayda ~21 trading günü

        return None

    def _extract_target_price(self, command: str) -> Optional[float]:
        """
        Hedef fiyatı çıkar
        """
        # $75, 75$, 75 dolar gibi formatlar
        patterns = [
            r'\$(\d+(?:\.\d+)?)',  # $75 veya $75.50
            r'(\d+(?:\.\d+)?)\s*(?:dolar|dollar|\$)',  # 75 dolar
            r'hedef[:\s]+(\d+(?:\.\d+)?)',  # hedef: 75
        ]

        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass

        return None

    def is_valid_command(self, command: str) -> bool:
        """
        Komutun geçerli olup olmadığını kontrol et

        Args:
            command: Kullanıcı komutu

        Returns:
            bool: Geçerli ise True
        """
        if not command or len(command.strip()) < 3:
            return False

        # En az bir asset veya analiz tipi içermeli
        command = command.lower()

        has_asset = any(asset in command for asset in self.assets)
        has_analysis = any(analysis in command for analysis in self.analysis_types)

        return has_asset or has_analysis


class CommandExamples:
    """
    Örnek komutlar
    """

    @staticmethod
    def get_examples() -> List[str]:
        """
        Örnek komutları döndür

        Returns:
            list: Örnek komutlar
        """
        examples = [
            "Gümüş için 2026 projeksiyonu yap",
            "Silver monte carlo simülasyonu",
            "Altın teknik analizi",
            "Gümüş için strateji öner",
            "Silver backtest son 3 yıl",
            "Gümüş $100 hedefine ulaşma olasılığı",
            "Gold silver ratio analizi",
            "Gümüş tam analiz",
            "Silver destek direnç seviyeleri",
            "Altın için bull bear senaryoları",
        ]

        return examples

    @staticmethod
    def print_examples():
        """
        Örnekleri yazdır
        """
        print("=" * 70)
        print("📝 ÖRNEK KOMUTLAR")
        print("=" * 70)

        for idx, example in enumerate(CommandExamples.get_examples(), 1):
            print(f"{idx}. {example}")

        print("=" * 70)