"""
Yahoo Finance'den veri çekme modülü
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Union
from pathlib import Path

from config.settings import DATA_CONFIG, YAHOO_CONFIG
from config.asset_config import get_ticker, get_asset_config, get_ticker_alternatives  # ← BURAYA EKLE
from utils.logger import logger
from utils.validators import validate_ticker, validate_asset_name, validate_price_data
from utils.helpers import calculate_date_range


class DataCollector:
    """
    Yahoo Finance veri çekici sınıfı
    """

    def __init__(self):
        """
        DataCollector başlatıcı
        """
        self.timeout = YAHOO_CONFIG['timeout']
        self.retry_count = YAHOO_CONFIG['retry_count']
        logger.info("DataCollector başlatıldı")

    def fetch_price_data(
            self,
            asset_name: str,
            period: str = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Asset için fiyat verisi çek

        Args:
            asset_name: 'silver' veya 'gold'
            period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y'
            start_date: Başlangıç tarihi (opsiyonel)
            end_date: Bitiş tarihi (opsiyonel)

        Returns:
            pd.DataFrame: Fiyat verisi veya None
        """
        # Asset validasyonu
        if not validate_asset_name(asset_name):
            return None

        # Import ekliyoruz (dosyanın başında olmalı, ama burada hatırlatma için)

        # Ana ticker al
        ticker = get_ticker(asset_name)

        # Alternatif ticker'ları da al
        alternative_tickers = [ticker] + get_ticker_alternatives(asset_name)

        logger.info(f"Veri çekiliyor: {asset_name} (Ticker'lar: {alternative_tickers})")

        # Period veya tarih aralığı kullan
        if period and not start_date:
            if period not in DATA_CONFIG:
                period = DATA_CONFIG['default_period']

        # Her ticker'ı sırayla dene
        for current_ticker in alternative_tickers:
            logger.info(f"Deneniyor: {current_ticker}")

            # Retry mekanizması ile veri çek
            for attempt in range(self.retry_count):
                try:
                    if start_date and end_date:
                        # Tarih aralığı ile çek
                        data = yf.download(
                            current_ticker,
                            start=start_date,
                            end=end_date,
                            progress=False,
                            timeout=self.timeout,
                            auto_adjust=True  # FutureWarning'i önlemek için
                        )
                    else:
                        # Period ile çek
                        data = yf.download(
                            current_ticker,
                            period=period or DATA_CONFIG['default_period'],
                            progress=False,
                            timeout=self.timeout,
                            auto_adjust=True  # FutureWarning'i önlemek için
                        )

                    if data.empty:
                        logger.warning(f"Veri boş geldi: {current_ticker}")
                        break  # Bu ticker çalışmadı, sonrakini dene

                    # Veri validasyonu
                    if not validate_price_data(data, asset_name):
                        logger.warning(f"Veri doğrulaması başarısız: {current_ticker}")
                        break

                    logger.info(f"✅ Veri başarıyla çekildi: {len(data)} satır ({current_ticker})")
                    return data

                except Exception as e:
                    logger.warning(f"Deneme {attempt + 1}/{self.retry_count} başarısız: {str(e)}")
                    if attempt == self.retry_count - 1:
                        logger.warning(f"Ticker başarısız: {current_ticker}")
                        break  # Bu ticker çalışmadı, sonrakini dene

        logger.error(f"Hiçbir ticker'dan veri çekilemedi: {alternative_tickers}")
        return None

    def get_realtime_price(self, asset_name: str) -> Optional[float]:
        """
        Anlık fiyat al

        Args:
            asset_name: 'silver' veya 'gold'

        Returns:
            float: Anlık fiyat veya None
        """
        if not validate_asset_name(asset_name):
            return None

        ticker = get_ticker(asset_name)

        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            # Farklı fiyat alanlarını dene
            price = info.get('regularMarketPrice') or \
                    info.get('currentPrice') or \
                    info.get('previousClose')

            if price:
                logger.info(f"Anlık fiyat: {asset_name} = ${price:.2f}")
                return float(price)
            else:
                logger.warning(f"Anlık fiyat alınamadı: {ticker}")
                return None

        except Exception as e:
            logger.error(f"Anlık fiyat hatası: {ticker} - {str(e)}")
            return None

    def get_historical_data(
            self,
            asset_name: str,
            years: int = 10
    ) -> Optional[pd.DataFrame]:
        """
        Geçmiş veri al (yıl bazında)

        Args:
            asset_name: 'silver' veya 'gold'
            years: Kaç yıl geçmiş veri

        Returns:
            pd.DataFrame: Geçmiş veri
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        return self.fetch_price_data(
            asset_name=asset_name,
            start_date=start_date,
            end_date=end_date
        )

    def get_multiple_assets(
            self,
            asset_names: list[str],
            period: str = '10y'
    ) -> dict[str, pd.DataFrame]:
        """
        Birden fazla asset için veri çek

        Args:
            asset_names: Asset isimleri listesi
            period: Zaman periyodu

        Returns:
            dict: {asset_name: DataFrame}
        """
        results = {}

        for asset_name in asset_names:
            logger.info(f"Veri çekiliyor: {asset_name}")
            data = self.fetch_price_data(asset_name, period=period)

            if data is not None:
                results[asset_name] = data
            else:
                logger.warning(f"Veri çekilemedi: {asset_name}")

        return results

    def get_asset_info(self, asset_name: str) -> Optional[dict]:
        """
        Asset hakkında genel bilgi al

        Args:
            asset_name: 'silver' veya 'gold'

        Returns:
            dict: Asset bilgileri
        """
        if not validate_asset_name(asset_name):
            return None

        ticker = get_ticker(asset_name)

        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            asset_info = {
                'symbol': ticker,
                'name': info.get('shortName', asset_name),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'COMEX'),
                'current_price': info.get('regularMarketPrice'),
                'previous_close': info.get('previousClose'),
                'day_high': info.get('dayHigh'),
                'day_low': info.get('dayLow'),
                '52week_high': info.get('fiftyTwoWeekHigh'),
                '52week_low': info.get('fiftyTwoWeekLow'),
            }

            logger.info(f"Asset bilgisi alındı: {asset_name}")
            return asset_info

        except Exception as e:
            logger.error(f"Asset bilgisi hatası: {ticker} - {str(e)}")
            return None