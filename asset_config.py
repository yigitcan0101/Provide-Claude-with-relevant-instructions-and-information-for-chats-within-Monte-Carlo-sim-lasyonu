"""
Metal asset'leri için özel konfigürasyon
"""

# Asset tanımlamaları
ASSETS = {
    'silver': {
        'ticker': 'SI=F',  # Silver Futures (COMEX) - GÜNCEL!
        'ticker_alternatives': ['SLV', 'XAGUSD=X'],  # Alternatifler
        'name': 'Gümüş',
        'symbol': 'XAG/USD',
        'currency': 'USD',
        'unit': 'ons',
        'min_price': 10.0,
        'max_price': 200.0,
        'typical_volatility': 0.25,  # %25 yıllık
    },
    'gold': {
        'ticker': 'GC=F',  # Gold Futures (COMEX) - GÜNCEL!
        'ticker_alternatives': ['GLD', 'XAUUSD=X'],  # Alternatifler
        'name': 'Altın',
        'symbol': 'XAU/USD',
        'currency': 'USD',
        'unit': 'ons',
        'min_price': 1000.0,
        'max_price': 5000.0,
        'typical_volatility': 0.15,  # %15 yıllık
    }
}

# Gold-Silver Ratio ayarları
GOLD_SILVER_RATIO = {
    'historical_avg': 70,
    'high_threshold': 80,  # Gümüş ucuz
    'low_threshold': 60,   # Altın ucuz
}

# Asset validation
def get_asset_config(asset_name):
    """
    Asset konfigürasyonunu getir

    Args:
        asset_name (str): 'silver' veya 'gold'

    Returns:
        dict: Asset konfigürasyonu
    """
    asset_name = asset_name.lower()
    if asset_name not in ASSETS:
        raise ValueError(f"Geçersiz asset: {asset_name}. Geçerli değerler: {list(ASSETS.keys())}")
    return ASSETS[asset_name]

def get_ticker(asset_name):
    """
    Asset için Yahoo Finance ticker'ı getir

    Args:
        asset_name (str): 'silver' veya 'gold'

    Returns:
        str: Ticker sembolü
    """
    return get_asset_config(asset_name)['ticker']

def get_ticker_alternatives(asset_name):
    """
    Asset için alternatif ticker'ları getir

    Args:
        asset_name (str): 'silver' veya 'gold'

    Returns:
        list: Alternatif ticker sembolleri
    """
    return get_asset_config(asset_name).get('ticker_alternatives', [])