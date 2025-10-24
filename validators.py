"""
Veri doğrulama fonksiyonları
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from utils.logger import logger


def validate_ticker(ticker: str) -> bool:
    """
    Ticker sembolünün geçerli olup olmadığını kontrol et

    Args:
        ticker: Yahoo Finance ticker sembolü

    Returns:
        bool: Geçerli ise True
    """
    # Import burada yapıyoruz (circular import önlemek için)
    from config.asset_config import ASSETS

    valid_tickers = [asset['ticker'] for asset in ASSETS.values()]

    if ticker not in valid_tickers:
        logger.warning(f"Geçersiz ticker: {ticker}. Geçerli: {valid_tickers}")
        return False

    return True


def validate_asset_name(asset_name: str) -> bool:
    """
    Asset adının geçerli olup olmadığını kontrol et

    Args:
        asset_name: 'silver' veya 'gold'

    Returns:
        bool: Geçerli ise True
    """
    # Import burada yapıyoruz (circular import önlemek için)
    from config.asset_config import ASSETS

    asset_name = asset_name.lower()

    if asset_name not in ASSETS:
        logger.warning(f"Geçersiz asset: {asset_name}. Geçerli: {list(ASSETS.keys())}")
        return False

    return True


def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """
    Tarih aralığının geçerli olup olmadığını kontrol et

    Args:
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi

    Returns:
        bool: Geçerli ise True
    """
    if start_date >= end_date:
        logger.error(f"Geçersiz tarih aralığı: {start_date} >= {end_date}")
        return False

    if end_date > datetime.now():
        logger.warning(f"Bitiş tarihi gelecekte: {end_date}")
        return False

    # Minimum 30 günlük veri olmalı
    if (end_date - start_date).days < 30:
        logger.error(f"Tarih aralığı çok kısa: {(end_date - start_date).days} gün")
        return False

    return True


def validate_price_data(data: pd.DataFrame, asset_name: str) -> bool:
    """
    Fiyat verisinin geçerli olup olmadığını kontrol et

    Args:
        data: Fiyat verisi DataFrame
        asset_name: Asset adı ('silver' veya 'gold')

    Returns:
        bool: Geçerli ise True
    """
    # Import burada yapıyoruz (circular import önlemek için)
    from config.asset_config import ASSETS

    # None kontrolü
    if data is None:
        logger.error("Veri None!")
        return False

    # DataFrame kontrolü
    if not isinstance(data, pd.DataFrame):
        logger.error(f"Veri DataFrame değil: {type(data)}")
        return False

    # Boşluk kontrolü
    if len(data) == 0:
        logger.error("Veri boş!")
        return False

    # Gerekli kolonlar
    required_columns = ['Close']
    for col in required_columns:
        if col not in data.columns:
            logger.error(f"Eksik kolon: {col}")
            return False

    # NaN kontrolü
    nan_count = data['Close'].isna().sum()
    if isinstance(nan_count, pd.Series):
        nan_count = int(nan_count.iloc[0])
    else:
        nan_count = int(nan_count)

    total_rows = len(data)
    nan_ratio = nan_count / total_rows if total_rows > 0 else 0

    if nan_ratio > 0.1:  # %10'dan fazla NaN
        logger.error(f"Çok fazla eksik veri: {nan_count} / {total_rows} (%{nan_ratio * 100:.1f})")
        return False

    # Fiyat aralığı kontrolü
    try:
        asset_config = ASSETS.get(asset_name.lower())
        if asset_config:
            min_price = asset_config['min_price']
            max_price = asset_config['max_price']

            # Min/Max'ı float'a çevir
            min_value = data['Close'].min()
            max_value = data['Close'].max()
            actual_min = float(min_value.iloc[0] if isinstance(min_value, pd.Series) else min_value)
            actual_max = float(max_value.iloc[0] if isinstance(max_value, pd.Series) else max_value)

            # Sadece uyarı ver, False döndürme
            if actual_min < min_price or actual_max > max_price:
                logger.warning(
                    f"Fiyat aralığı dışında: "
                    f"Min={actual_min:.2f}, Max={actual_max:.2f} "
                    f"(Beklenen: {min_price}-{max_price})"
                )
    except Exception as e:
        logger.warning(f"Fiyat aralığı kontrolü başarısız: {str(e)}")

    logger.info(f"✅ Veri doğrulandı: {total_rows} satır, {nan_count} NaN")
    return True


def validate_monte_carlo_params(iterations: int, days: int) -> bool:
    """
    Monte Carlo parametrelerinin geçerli olup olmadığını kontrol et

    Args:
        iterations: İterasyon sayısı
        days: Projeksiyon gün sayısı

    Returns:
        bool: Geçerli ise True
    """
    if iterations < 100:
        logger.error(f"Çok az iterasyon: {iterations} (min: 100)")
        return False

    if iterations > 100000:
        logger.warning(f"Çok fazla iterasyon: {iterations} (uzun sürebilir)")

    if days < 1 or days > 1000:
        logger.error(f"Geçersiz gün sayısı: {days} (1-1000 arası olmalı)")
        return False

    return True