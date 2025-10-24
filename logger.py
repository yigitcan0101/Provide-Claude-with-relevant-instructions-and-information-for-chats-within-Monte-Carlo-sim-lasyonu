"""
Merkezi logging sistemi
"""
import logging
import sys
from pathlib import Path
from config.settings import LOG_CONFIG


def setup_logger(name: str = 'FinancialMetalAnalysis') -> logging.Logger:
    """
    Logger oluştur ve yapılandır

    Args:
        name: Logger adı

    Returns:
        logging.Logger: Yapılandırılmış logger
    """
    logger = logging.getLogger(name)

    # Eğer daha önce handler eklenmişse, tekrar ekleme
    if logger.handlers:
        return logger

    logger.setLevel(LOG_CONFIG['level'])

    # Formatter
    formatter = logging.Formatter(LOG_CONFIG['format'])

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(
        LOG_CONFIG['file'],
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger()


def log_function_call(func):
    """
    Fonksiyon çağrılarını loglayan decorator

    Usage:
        @log_function_call
        def my_function(x, y):
            return x + y
    """

    def wrapper(*args, **kwargs):
        logger.debug(f"Çağrıldı: {func.__name__} args={args} kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Tamamlandı: {func.__name__} sonuç={result}")
            return result
        except Exception as e:
            logger.error(f"Hata: {func.__name__} - {str(e)}", exc_info=True)
            raise

    return wrapper