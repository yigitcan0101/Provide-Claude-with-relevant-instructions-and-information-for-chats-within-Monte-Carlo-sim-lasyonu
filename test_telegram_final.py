# test_telegram_final.py

import requests

TOKEN = "8201317145:AAH71jErrLu4x87DxPQ35-pupEWQxJ7zD3I"
CHAT_ID = "8437395019"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

payload = {
    'chat_id': CHAT_ID,
    'text': '🎉 <b>Test Mesajı</b>\n\nBot başarıyla çalışıyor!',
    'parse_mode': 'HTML'
}

print("📤 Mesaj gönderiliyor...")
print(f"Token: {TOKEN[:20]}...")
print(f"Chat ID: {CHAT_ID}")
print()

try:
    response = requests.post(url, json=payload, timeout=10)

    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{response.json()}\n")

    if response.status_code == 200:
        print("✅ BAŞARILI! Telegram'ı kontrol et.")
    else:
        print("❌ HATA!")
        error = response.json()
        print(f"Açıklama: {error.get('description', 'Bilinmiyor')}")

except Exception as e:
    print(f"❌ Bağlantı hatası: {e}")