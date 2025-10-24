"""
Support/Resistance Test
"""
from data.data_collector import DataCollector
from strategy.support_resistance import SupportResistance

# Veri çek
collector = DataCollector()
data = collector.fetch_price_data('silver', period='2y')

if data is not None:
    print("=" * 70)
    print("🎯 DESTEK/DİRENÇ ANALİZİ")
    print("=" * 70)

    # Support/Resistance
    sr = SupportResistance()

    # Seviyeleri bul
    levels = sr.find_support_resistance_levels(data, num_levels=3)

    print(f"\n💰 Mevcut Fiyat: ${levels['current_price']:.2f}")

    print("\n📉 DESTEK SEVİYELERİ:")
    for i, support in enumerate(levels['support'], 1):
        strength = sr.calculate_strength(data, support, 'support')
        print(f"  S{i}: ${support:.2f} (Güç: {strength} test)")

    print("\n📈 DİRENÇ SEVİYELERİ:")
    for i, resistance in enumerate(levels['resistance'], 1):
        strength = sr.calculate_strength(data, resistance, 'resistance')
        print(f"  R{i}: ${resistance:.2f} (Güç: {strength} test)")

    # En yakın seviyeler
    print("\n" + "=" * 70)
    print("🎯 EN YAKIN SEVİYELER")
    print("=" * 70)

    nearest = sr.find_nearest_support_resistance(data)
    print(f"\nEn Yakın Destek: ${nearest['nearest_support']:.2f}")
    print(f"  Mesafe: {nearest['support_distance_pct']:.2f}% aşağıda")

    print(f"\nEn Yakın Direnç: ${nearest['nearest_resistance']:.2f}")
    print(f"  Mesafe: {nearest['resistance_distance_pct']:.2f}% yukarıda")

    # Kırılım potansiyeli
    print("\n" + "=" * 70)
    print("⚡ KIRILIM POTANSİYELİ ANALİZİ")
    print("=" * 70)

    breakout = sr.get_breakout_potential(data)

    print(f"\nDirenç Kırılım Potansiyeli: {breakout['resistance']['breakout_potential']}")
    print(f"  Direnç: ${breakout['resistance']['price']:.2f}")
    print(f"  Mesafe: {breakout['resistance']['distance_pct']:.2f}%")
    print(f"  Güç: {breakout['resistance']['strength']} test")

    print(f"\nDestek Kırılım Riski: {breakout['support']['breakdown_risk']}")
    print(f"  Destek: ${breakout['support']['price']:.2f}")
    print(f"  Mesafe: {breakout['support']['distance_pct']:.2f}%")
    print(f"  Güç: {breakout['support']['strength']} test")

    print(f"\nVolatilite (Son 20 gün): {breakout['volatility']:.2%}")

    # Pozisyon kontrolü
    print("\n" + "=" * 70)
    print("📍 FİYAT POZİSYONU")
    print("=" * 70)

    if sr.is_at_support(data):
        print("✅ Fiyat DESTEK seviyesinde! (Alım fırsatı olabilir)")
    elif sr.is_at_resistance(data):
        print("⚠️ Fiyat DİRENÇ seviyesinde! (Risk bölgesi)")
    else:
        print("⚪ Fiyat destek-direnç arasında (Nötr bölge)")

    print("=" * 70)

else:
    print("❌ Veri çekilemedi!")