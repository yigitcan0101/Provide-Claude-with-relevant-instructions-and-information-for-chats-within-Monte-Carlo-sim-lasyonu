"""
Genel sistem ayarları ve sabitler
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Proje kök dizini
BASE_DIR = Path(__file__).resolve().parent.parent

# Veri ayarları
DATA_CONFIG = {
    'source': 'yahoo',
    'default_period': '10y',  # 10 yıl geçmiş veri
    'cache_duration_hours': int(os.getenv('CACHE_DURATION_HOURS', 6)),
}

# Yahoo Finance ayarları
YAHOO_CONFIG = {
    'rate_limit': int(os.getenv('YAHOO_RATE_LIMIT', 2000)),
    'timeout': 30,  # saniye
    'retry_count': 3,
}

# Monte Carlo ayarları
MONTE_CARLO_CONFIG = {
    'iterations': 10000,
    'trading_days_per_year': 252,
    'projection_days': 252,  # 1 yıl
    'confidence_levels': [0.05, 0.50, 0.95],  # %5, %50, %95
}

# Teknik analiz ayarları
TECHNICAL_CONFIG = {
    'ema_periods': [20, 50, 200],
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'atr_period': 14,
    'fibonacci_levels': [0.236, 0.382, 0.5, 0.618, 0.786],
}

# Strateji ayarları
STRATEGY_CONFIG = {
    'entry_levels': 3,  # 3 kademeli alım
    'stop_loss_multiplier': 2.0,  # ATR x 2
    'risk_per_trade': 0.02,  # Sermayenin %2'si
    'min_risk_reward': 2.0,  # Minimum 1:2 R:R
    'kelly_fraction': 0.5,  # Kelly %50 (konservatif)
}

# Backtest ayarları
BACKTEST_CONFIG = {
    'initial_capital': float(os.getenv('BACKTEST_INITIAL_CAPITAL', 10000)),
    'commission': float(os.getenv('BACKTEST_COMMISSION', 0.001)),
    'slippage': float(os.getenv('BACKTEST_SLIPPAGE', 0.0005)),
    'test_period_years': 3,
}

# Telegram ayarları (henüz token yok)
TELEGRAM_CONFIG = {
    'enabled': False,  # Bot oluşturulunca True yapacağız
    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
    'max_message_length': 4096,
    'image_format': 'PNG',
}

# Çıktı ayarları
OUTPUT_CONFIG = {
    'results_dir': BASE_DIR / 'results',
    'charts_dir': BASE_DIR / 'results' / 'charts',
    'reports_dir': BASE_DIR / 'results' / 'reports',
    'backtest_dir': BASE_DIR / 'results' / 'backtest_results',
    'chart_dpi': 100,
    'chart_size': (10, 6),
}

# Log ayarları
LOG_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': BASE_DIR / 'app.log',
}

# Gerekli dizinleri oluştur
for directory in [
    OUTPUT_CONFIG['results_dir'],
    OUTPUT_CONFIG['charts_dir'],
    OUTPUT_CONFIG['reports_dir'],
    OUTPUT_CONFIG['backtest_dir'],
]:
    directory.mkdir(parents=True, exist_ok=True)

# Cache dizini
CACHE_DIR = BASE_DIR / 'cache'
CACHE_DIR.mkdir(exist_ok=True)