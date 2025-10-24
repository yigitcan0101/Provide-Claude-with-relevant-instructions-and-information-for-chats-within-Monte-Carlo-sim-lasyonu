"""
Telegram bot konfigürasyonu
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Ayarları
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Telegram özellikleri
TELEGRAM_CONFIG = {
    'enabled': bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
    'bot_token': TELEGRAM_BOT_TOKEN,
    'chat_id': TELEGRAM_CHAT_ID,
    'max_message_length': 4096,
    'parse_mode': 'HTML',  # HTML veya Markdown
    'disable_notification': False,
}


def is_telegram_enabled() -> bool:
    """
    Telegram bot aktif mi kontrol et

    Returns:
        bool: Aktif ise True
    """
    return TELEGRAM_CONFIG['enabled']


def get_bot_token() -> str:
    """
    Bot token'ı getir

    Returns:
        str: Bot token
    """
    return TELEGRAM_CONFIG['bot_token']


def get_chat_id() -> str:
    """
    Chat ID'yi getir

    Returns:
        str: Chat ID
    """
    return TELEGRAM_CONFIG['chat_id']