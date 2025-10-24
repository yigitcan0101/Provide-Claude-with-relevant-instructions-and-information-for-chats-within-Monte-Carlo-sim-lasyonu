"""
Telegram mesaj ve grafik gönderimi (BASİT VERSİYON)
"""
import requests
from pathlib import Path
from typing import Optional, List

from utils.logger import logger
from config.telegram_config import TELEGRAM_CONFIG, is_telegram_enabled


class TelegramSender:
    """
    Telegram bot ile mesaj ve dosya gönderimi
    """

    def __init__(self):
        self.enabled = is_telegram_enabled()
        self.bot_token = TELEGRAM_CONFIG['bot_token']
        self.chat_id = TELEGRAM_CONFIG['chat_id']
        self.max_length = TELEGRAM_CONFIG['max_message_length']

        if self.enabled:
            logger.info("TelegramSender başlatıldı (BOT AKTİF)")
        else:
            logger.warning("TelegramSender başlatıldı (BOT PASİF)")

    def send_message(self, message: str) -> bool:
        """Basit mesaj gönder (Plain text)"""
        if not self.enabled:
            return False

        # Uzun mesajları böl
        chunks = self._split_message(message)

        for chunk in chunks:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {'chat_id': self.chat_id, 'text': chunk}

            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code != 200:
                    logger.error(f"Telegram hatası: {response.text}")
                    return False
            except Exception as e:
                logger.error(f"Telegram gönderim hatası: {e}")
                return False

        logger.info("Telegram mesajı gönderildi")
        return True

    def send_photo(self, photo_path: str, caption: Optional[str] = None) -> bool:
        """Fotoğraf gönder"""
        if not self.enabled:
            return False

        photo_file = Path(photo_path)
        if not photo_file.exists():
            logger.error(f"Fotoğraf bulunamadı: {photo_path}")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"

        try:
            with open(photo_file, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': self.chat_id}
                if caption:
                    data['caption'] = caption

                response = requests.post(url, data=data, files=files, timeout=30)

                if response.status_code == 200:
                    logger.info(f"Fotoğraf gönderildi: {photo_path}")
                    return True
                else:
                    logger.error(f"Fotoğraf hatası: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Fotoğraf gönderim hatası: {e}")
            return False

    def send_media_group(self, photo_paths: List[str], caption: Optional[str] = None) -> bool:
        """Birden fazla fotoğraf gönder"""
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMediaGroup"
        media = []
        files = {}

        for idx, photo_path in enumerate(photo_paths):
            photo_file = Path(photo_path)
            if not photo_file.exists():
                continue

            file_key = f'photo{idx}'
            files[file_key] = open(photo_file, 'rb')

            media_item = {'type': 'photo', 'media': f'attach://{file_key}'}
            if idx == 0 and caption:
                media_item['caption'] = caption

            media.append(media_item)

        if not media:
            return False

        try:
            import json
            data = {'chat_id': self.chat_id, 'media': json.dumps(media)}
            response = requests.post(url, data=data, files=files, timeout=60)

            for f in files.values():
                f.close()

            if response.status_code == 200:
                logger.info(f"Media group gönderildi: {len(media)} fotoğraf")
                return True
            else:
                logger.error(f"Media group hatası: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Media group hatası: {e}")
            for f in files.values():
                try:
                    f.close()
                except:
                    pass
            return False

    def send_full_report(self, report_text: str, chart_paths: List[str]) -> bool:
        """Tam rapor gönder (metin + grafikler)"""
        text_success = self.send_message(report_text)
        charts_success = self.send_media_group(chart_paths, caption="📊 Analiz Grafikleri")
        return text_success and charts_success

    def _split_message(self, message: str) -> List[str]:
        """Uzun mesajı böl"""
        if len(message) <= self.max_length:
            return [message]

        chunks = []
        lines = message.split('\n')
        current_chunk = []
        current_length = 0

        for line in lines:
            line_length = len(line) + 1

            if current_length + line_length > self.max_length:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks