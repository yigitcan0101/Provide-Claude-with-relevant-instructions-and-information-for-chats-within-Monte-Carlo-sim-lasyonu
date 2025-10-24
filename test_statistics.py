"""
Statistical Engine test
"""
import pandas as pd
from data.data_collector import DataCollector
from analysis.statistical_engine import StatisticalEngine

# Veri çek
print("Veri çekiliyor...")
collector = DataCollector()
data = collector.fetch_price_data('silver', period='1y')

if data is not None:
    # Multi-index düzleştir
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    print(f"✅ {len(data)} satır veri alındı\n")

    # Statistical Engine
    engine = StatisticalEngine()

    # İstatistikleri hesapla
    print("İstatistikler hesaplanıyor...\n")
    stats = engine.get_full_statistics(data)

    # Sonuçları yazdır
    print("=" * 50)
    print("📊 İSTATİSTİKSEL ANALİZ SONUÇLARI")
    print("=" * 50)
    print(f"Günlük Ortalama Getiri: {stats['mean_daily_return']:.4%}")
    print(f"Günlük Volatilite: {stats['std_daily_return']:.4%}")
    print(f"Yıllık Getiri: {stats['annual_return']:.2%}")
    print(f"Yıllık Volatilite: {stats['annual_volatility']:.2%}")
    print(f"Sharpe Ratio: {stats['sharpe_ratio']:.4f}")
    print(f"Güncel Fiyat: ${stats['current_price']:.2f}")
    print("=" * 50)
else:
    print("❌ Veri çekilemedi!")