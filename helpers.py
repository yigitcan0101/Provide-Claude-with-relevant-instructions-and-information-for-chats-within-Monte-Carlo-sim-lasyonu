"""
Yardımcı fonksiyonlar
"""
from datetime import datetime, timedelta
from typing import Union, Optional
import pandas as pd
from utils.logger import logger


def format_currency(value: float, currency: str = 'USD') -> str:
    """
    Para birimi formatı

    Args:
        value: Sayısal değer
        currency: Para birimi

    Returns:
        str: Formatlanmış string ($28.40)
    """
    if currency == 'USD':
        return f"${value:,.2f}"
    return f"{value:,.2f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Yüzde formatı

    Args:
        value: Sayısal değer (0.234 = %23.4)
        decimals: Ondalık basamak sayısı

    Returns:
        str: Formatlanmış string (%23.40)
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_date_range(period: str = '10y') -> tuple[datetime, datetime]:
    """
    Period string'inden tarih aralığı hesapla

    Args:
        period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'

    Returns:
        tuple: (start_date, end_date)
    """
    end_date = datetime.now()

    period_map = {
        '1d': timedelta(days=1),
        '5d': timedelta(days=5),
        '1mo': timedelta(days=30),
        '3mo': timedelta(days=90),
        '6mo': timedelta(days=180),
        '1y': timedelta(days=365),
        '2y': timedelta(days=730),
        '5y': timedelta(days=1825),
        '10y': timedelta(days=3650),
    }

    if period == 'ytd':
        start_date = datetime(end_date.year, 1, 1)
    elif period == 'max':
        start_date = datetime(1990, 1, 1)
    elif period in period_map:
        start_date = end_date - period_map[period]
    else:
        logger.warning(f"Bilinmeyen period: {period}, 10y kullanılıyor")
        start_date = end_date - timedelta(days=3650)

    return start_date, end_date


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame'i temizle (NaN, duplicates, vb.)

    Args:
        df: Temizlenecek DataFrame

    Returns:
        pd.DataFrame: Temizlenmiş DataFrame
    """
    logger.info(f"Temizlik öncesi: {len(df)} satır, {df.isna().sum().sum()} NaN")

    # Duplicate index temizle
    df = df[~df.index.duplicated(keep='first')]

    # NaN'leri forward fill ile doldur
    df = df.ffill()

    # Hala NaN varsa backward fill
    df = df.bfill()

    # Kalan NaN'leri sil
    df = df.dropna()

    logger.info(f"Temizlik sonrası: {len(df)} satır")

    return df


def calculate_trading_days(start_date: datetime, end_date: datetime) -> int:
    """
    İki tarih arasındaki trading gün sayısını hesapla

    Args:
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi

    Returns:
        int: Trading gün sayısı (yaklaşık)
    """
    total_days = (end_date - start_date).days
    # Yılda yaklaşık 252 trading günü var (365 * 5/7 ≈ 261, tatiller -%5)
    trading_days = int(total_days * 252 / 365)
    return trading_days


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Güvenli bölme (sıfıra bölme hatası önleme)

    Args:
        numerator: Bölünen
        denominator: Bölen
        default: Hata durumunda döndürülecek değer

    Returns:
        float: Bölme sonucu veya default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default


def timestamp_to_str(timestamp: Union[datetime, pd.Timestamp],
                     format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Timestamp'i string'e çevir

    Args:
        timestamp: Datetime veya Pandas Timestamp
        format: Strftime formatı

    Returns:
        str: Formatlanmış tarih
    """
    if isinstance(timestamp, pd.Timestamp):
        timestamp = timestamp.to_pydatetime()

    return timestamp.strftime(format)