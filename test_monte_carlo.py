"""
Monte Carlo Simulator test
"""
import pandas as pd
import numpy as np
from data.data_collector import DataCollector
from analysis.monte_carlo_simulator import MonteCarloSimulator

# Veri çek
print("Veri çekiliyor...")
collector = DataCollector()
data = collector.fetch_price_data('silver', period='1y')

if data is not None:
    print(f"✅ {len(data)} satır veri alındı\n")

    # Monte Carlo Simulator
    simulator = MonteCarloSimulator()

    # ========================================
    # TEST 1: HEDEF FİYAT BELİRTMEDEN
    # ========================================
    print("="*60)
    print("TEST 1: Hedef Fiyat Belirtmeden (Serbest Projeksiyon)")
    print("="*60)
    print("Monte Carlo simülasyonu çalışıyor...")
    print("(10,000 iterasyon x 252 gün)\n")

    results = simulator.run_full_analysis(data=data)

    print("🎲 MONTE CARLO SİMÜLASYON SONUÇLARI (1 Yıl)")
    print("="*60)
    print(f"Mevcut Fiyat: ${results['current_price']:.2f}")
    print()
    print(f"Gelecek Fiyat Tahminleri:")
    print(f"  Medyan Beklenti: ${results['median_final_price']:.2f}")
    print(f"  Ortalama Beklenti: ${results['mean_final_price']:.2f}")
    print()
    print(f"Olasılık Aralıkları:")
    print(f"  %5 İhtimal (Çok Düşük): ${results['percentile_5']:.2f}")
    print(f"  %25 İhtimal (Düşük): ${np.percentile(results['price_paths'][:,-1], 25):.2f}")
    print(f"  %50 İhtimal (Medyan): ${results['percentile_50']:.2f}")
    print(f"  %75 İhtimal (Yüksek): ${results['target_analysis']['percentile_75_target']:.2f}")
    print(f"  %90 İhtimal (Çok Yüksek): ${results['target_analysis']['percentile_90_target']:.2f}")
    print(f"  %95 İhtimal (En İyi): ${results['percentile_95']:.2f}")
    print()
    print(f"Risk Metrikleri:")
    print(f"  VaR (%5): ${results['risk_metrics']['var_5']:.2f} (en kötü %5'lik senaryoda düşüş)")
    print(f"  VaR (%1): ${results['risk_metrics']['var_1']:.2f} (en kötü %1'lik senaryoda düşüş)")
    print("="*60)

    # ========================================
    # TEST 2: KULLANICI HEDEF FİYATI BELİRTİNCE
    # ========================================
    print("\n\n")
    print("="*60)
    print("TEST 2: Kullanıcı Hedef Fiyatı ile ($100)")
    print("="*60)
    print("Monte Carlo simülasyonu çalışıyor...\n")

    user_target = 100.0
    results2 = simulator.run_full_analysis(
        data=data,
        target_price=user_target
    )

    print("🎲 MONTE CARLO SİMÜLASYON SONUÇLARI (1 Yıl)")
    print("="*60)
    print(f"Mevcut Fiyat: ${results2['current_price']:.2f}")
    print(f"Medyan Beklenti: ${results2['median_final_price']:.2f}")
    print()
    print(f"🎯 KULLANICI HEDEFİ ANALİZİ:")
    print(f"  Hedef Fiyat: ${results2['target_analysis']['target_price']:.2f}")
    print(f"  Ulaşma Olasılığı: {results2['target_analysis']['probability']:.2%}")
    print()
    if results2['target_analysis']['probability'] < 0.05:
        print(f"  ⚠️  Değerlendirme: Çok düşük olasılık (<%5)")
    elif results2['target_analysis']['probability'] < 0.25:
        print(f"  ⚠️  Değerlendirme: Düşük olasılık (<%25)")
    elif results2['target_analysis']['probability'] < 0.50:
        print(f"  ⚡ Değerlendirme: Orta olasılık")
    else:
        print(f"  ✅ Değerlendirme: Yüksek olasılık")
    print("="*60)

    # ========================================
    # ÖZET
    # ========================================
    print("\n\n")
    print("="*60)
    print("📊 ÖZET BİLGİLER")
    print("="*60)
    print(f"Simülasyon Detayları:")
    print(f"  - İterasyon: {results['iterations']:,}")
    print(f"  - Gün Sayısı: {results['days']}")
    print(f"  - Yıllık Volatilite: {results['statistics']['annual_volatility']:.2%}")
    print(f"  - Yıllık Beklenen Getiri: {results['statistics']['annual_return']:.2%}")
    print(f"  - Sharpe Ratio: {results['statistics']['sharpe_ratio']:.4f}")
    print("="*60)

else:
    print("❌ Veri çekilemedi!")