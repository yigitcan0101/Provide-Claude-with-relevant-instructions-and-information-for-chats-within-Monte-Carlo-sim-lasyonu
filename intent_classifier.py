"""
Kullanıcı niyetini (intent) sınıflandırma
"""
from typing import Dict, List
from utils.logger import logger


class IntentClassifier:
    """
    Kullanıcı niyetini tespit eder
    """

    def __init__(self):
        """
        IntentClassifier başlatıcı
        """
        self.intents = {
            'price_query': ['fiyat', 'kaç', 'ne kadar', 'price', 'mevcut'],
            'analysis': ['analiz', 'analysis', 'incele', 'değerlendir'],
            'prediction': ['tahmin', 'projeksiyon', 'gelecek', 'predict', 'forecast'],
            'strategy': ['strateji', 'strategy', 'al', 'sat', 'giriş', 'buy', 'sell'],
            'comparison': ['karşılaştır', 'compare', 'fark', 'ratio', 'oran'],
            'backtest': ['test', 'backtest', 'geçmiş', 'performans'],
            'help': ['yardım', 'help', 'nasıl', 'örnek', 'komut'],
        }

        logger.info("IntentClassifier başlatıldı")

    def classify(self, command: str) -> str:
        """
        Komutu sınıflandır

        Args:
            command: Kullanıcı komutu

        Returns:
            str: Intent (niyet)
        """
        command = command.lower()

        # Her intent için kontrol et
        for intent, keywords in self.intents.items():
            if any(keyword in command for keyword in keywords):
                logger.info(f"Intent tespit edildi: {intent}")
                return intent

        # Varsayılan: analysis
        logger.info("Intent tespit edilemedi, varsayılan: analysis")
        return 'analysis'

    def get_confidence(self, command: str, intent: str) -> float:
        """
        Intent güven skorunu hesapla

        Args:
            command: Kullanıcı komutu
            intent: Tespit edilen intent

        Returns:
            float: Güven skoru (0-1 arası)
        """
        if intent not in self.intents:
            return 0.0

        command = command.lower()
        keywords = self.intents[intent]

        # Kaç tane anahtar kelime eşleşti
        matches = sum(1 for keyword in keywords if keyword in command)

        # Güven skoru
        confidence = min(matches / len(keywords), 1.0)

        return confidence

    def suggest_intent(self, command: str) -> List[Dict[str, any]]:
        """
        Olası intent'leri öner (skorlarla birlikte)

        Args:
            command: Kullanıcı komutu

        Returns:
            list: [{'intent': 'analysis', 'confidence': 0.8}, ...]
        """
        suggestions = []

        for intent in self.intents.keys():
            confidence = self.get_confidence(command, intent)

            if confidence > 0:
                suggestions.append({
                    'intent': intent,
                    'confidence': confidence
                })

        # Skoruna göre sırala
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)

        return suggestions