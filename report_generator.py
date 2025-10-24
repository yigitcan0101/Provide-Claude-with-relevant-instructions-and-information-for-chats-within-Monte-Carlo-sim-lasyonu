"""
5 bloklu rapor oluşturucu
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

from utils.logger import logger


class ReportGenerator:
    """
    Analiz raporu oluşturur (5 blok formatında)
    """

    def __init__(self):
        """
        ReportGenerator başlatıcı
        """
        logger.info("ReportGenerator başlatıldı")

    def generate_full_report(
            self,
            asset_name: str,
            current_price: float,
            technical_analysis: Dict,
            monte_carlo_results: Dict,
            strategy: Dict,
            scenarios: Optional[Dict] = None
    ) -> str:
        """
        Tam rapor oluştur (5 blok)

        Args:
            asset_name: Asset adı
            current_price: Mevcut fiyat
            technical_analysis: Teknik analiz sonuçları
            monte_carlo_results: Monte Carlo sonuçları
            strategy: Strateji önerisi
            scenarios: Senaryolar (opsiyonel)

        Returns:
            str: Formatlanmış rapor
        """
        report = []
        report.append("=" * 70)
        report.append(f"📊 {asset_name.upper()} ANALİZ RAPORU")
        report.append("=" * 70)
        report.append(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")

        # BLOK 1: FİYAT ÖZETİ
        report.append(self._block_1_price_summary(
            current_price,
            monte_carlo_results['statistics']
        ))

        # BLOK 2: TEKNİK ANALİZ
        report.append(self._block_2_technical_analysis(technical_analysis))

        # BLOK 3: MONTE CARLO SONUÇLARI
        report.append(self._block_3_monte_carlo(monte_carlo_results))

        # BLOK 4: STRATEJİ ÖNERİSİ
        report.append(self._block_4_strategy(strategy))

        # BLOK 5: ÖZET YORUM
        report.append(self._block_5_summary(
            technical_analysis,
            monte_carlo_results,
            strategy,
            scenarios
        ))

        report.append("=" * 70)
        report.append("✅ Rapor Oluşturuldu")
        report.append("=" * 70)

        full_report = "\n".join(report)
        logger.info("Tam rapor oluşturuldu")

        return full_report

    def _block_1_price_summary(
            self,
            current_price: float,
            statistics: Dict
    ) -> str:
        """
        BLOK 1: Fiyat Özeti
        """
        block = []
        block.append("=" * 70)
        block.append("1️⃣  FİYAT ÖZETİ")
        block.append("=" * 70)
        block.append(f"Mevcut Fiyat: ${current_price:.2f}")
        block.append(f"Günlük Ortalama Getiri: {statistics['mean_daily_return']:.4%}")
        block.append(f"Günlük Volatilite: {statistics['std_daily_return']:.4%}")
        block.append(f"Yıllık Volatilite: {statistics['annual_volatility']:.2%}")
        block.append(f"Yıllık Beklenen Getiri: {statistics['annual_return']:.2%}")
        block.append(f"Sharpe Ratio: {statistics['sharpe_ratio']:.4f}")
        block.append("")

        return "\n".join(block)

    def _block_2_technical_analysis(
            self,
            tech: Dict
    ) -> str:
        """
        BLOK 2: Teknik Analiz
        """
        block = []
        block.append("=" * 70)
        block.append("2️⃣  TEKNİK ANALİZ")
        block.append("=" * 70)

        # Trend
        block.append(f"📈 Trend: {tech['trend']['trend']}")
        block.append(f"   EMA20: ${tech['ema']['ema20']:.2f}")
        block.append(f"   EMA50: ${tech['ema']['ema50']:.2f}")
        block.append(f"   EMA200: ${tech['ema']['ema200']:.2f}")
        block.append("")

        # RSI
        block.append(f"⚡ RSI: {tech['rsi']['value']:.2f}")
        block.append(f"   Durum: {tech['rsi']['signal']}")
        block.append("")

        # MACD
        block.append(f"📊 MACD: {tech['macd']['interpretation']}")
        block.append(f"   MACD: {tech['macd']['macd']:.4f}")
        block.append(f"   Signal: {tech['macd']['signal']:.4f}")
        block.append("")

        # Destek/Direnç
        block.append(f"🎯 Fibonacci Seviyeleri:")
        fib = tech['fibonacci']
        block.append(f"   %61.8: ${fib['fib_0.618']:.2f}")
        block.append(f"   %50.0: ${fib['fib_0.5']:.2f}")
        block.append(f"   %38.2: ${fib['fib_0.382']:.2f}")
        block.append("")

        # Pivot Points
        block.append(f"🔄 Pivot Points:")
        pivots = tech['pivots']
        block.append(f"   R1: ${pivots['resistance_1']:.2f}")
        block.append(f"   PP: ${pivots['pivot']:.2f}")
        block.append(f"   S1: ${pivots['support_1']:.2f}")
        block.append("")

        return "\n".join(block)

    def _block_3_monte_carlo(
            self,
            mc_results: Dict
    ) -> str:
        """
        BLOK 3: Monte Carlo Sonuçları
        """
        block = []
        block.append("=" * 70)
        block.append("3️⃣  MONTE CARLO SONUÇLARI (1 Yıl Projeksiyonu)")
        block.append("=" * 70)
        block.append(f"İterasyon Sayısı: {mc_results['iterations']:,}")
        block.append(f"Projeksiyon Günü: {mc_results['days']}")
        block.append("")

        block.append(f"📊 Beklenen Fiyat Aralığı:")
        block.append(f"   Medyan: ${mc_results['median_final_price']:.2f}")
        block.append(f"   Ortalama: ${mc_results['mean_final_price']:.2f}")
        block.append("")

        block.append(f"📈 Olasılık Dağılımı:")
        block.append(f"   %5 İhtimal: ${mc_results['percentile_5']:.2f}")
        block.append(f"   %25 İhtimal: ${mc_results.get('percentile_25', mc_results['percentile_5']):.2f}")
        block.append(f"   %50 İhtimal (Medyan): ${mc_results['percentile_50']:.2f}")
        block.append(f"   %75 İhtimal: ${mc_results.get('percentile_75', mc_results['percentile_95']):.2f}")
        block.append(f"   %95 İhtimal: ${mc_results['percentile_95']:.2f}")
        block.append("")

        block.append(f"⚠️  Risk Metrikleri:")
        block.append(f"   VaR (5%): ${mc_results['risk_metrics']['var_5']:.2f}")
        block.append(f"   VaR (1%): ${mc_results['risk_metrics']['var_1']:.2f}")
        block.append("")

        # Hedef analizi varsa
        if 'target_analysis' in mc_results and mc_results['target_analysis'].get('user_defined'):
            block.append(f"🎯 Hedef Analizi:")
            block.append(f"   Hedef Fiyat: ${mc_results['target_analysis']['target_price']:.2f}")
            block.append(f"   Ulaşma Olasılığı: {mc_results['target_analysis']['probability']:.2%}")
            block.append("")

        return "\n".join(block)

    def _block_4_strategy(
            self,
            strategy: Dict
    ) -> str:
        """
        BLOK 4: Strateji Önerisi
        """
        block = []
        block.append("=" * 70)
        block.append("4️⃣  STRATEJİ ÖNERİSİ (3 Kademeli Alım)")
        block.append("=" * 70)

        for entry in strategy['entries']:
            block.append(f"\nKADEME {entry['level']}: ${entry['price']:.2f}")
            block.append(f"   Pozisyon Boyutu: %{entry['size_pct']:.1f}")
            block.append(f"   Açıklama: {entry['description']}")

        block.append(f"\n🛑 Stop-Loss: ${strategy['stop_loss']:.2f}")
        block.append(f"🎯 Target: ${strategy['target']:.2f}")
        block.append(f"📊 Risk/Reward Oranı: 1:{strategy['risk_reward_ratio']:.2f}")
        block.append("")

        if strategy.get('warning'):
            block.append(f"⚠️  UYARI: {strategy['warning']}")
            block.append("")

        return "\n".join(block)

    def _block_5_summary(
            self,
            tech: Dict,
            mc_results: Dict,
            strategy: Dict,
            scenarios: Optional[Dict]
    ) -> str:
        """
        BLOK 5: Özet Yorum
        """
        block = []
        block.append("=" * 70)
        block.append("5️⃣  ÖZET YORUM")
        block.append("=" * 70)

        # Teknik durum
        trend = tech['trend']['strength']
        rsi_status = tech['rsi']['status']
        macd_status = tech['macd']['status']

        block.append("📌 Teknik Yapı:")
        if trend in ['strong_bullish', 'bullish']:
            block.append("   ✅ Trend yükseliş yönünde")
        elif trend in ['strong_bearish', 'bearish']:
            block.append("   ❌ Trend düşüş yönünde")
        else:
            block.append("   ⚪ Trend belirsiz/yatay")

        if rsi_status == 'oversold':
            block.append("   ✅ RSI aşırı satımda (alım fırsatı olabilir)")
        elif rsi_status == 'overbought':
            block.append("   ⚠️  RSI aşırı alımda (dikkatli olunmalı)")

        if macd_status == 'bullish':
            block.append("   ✅ MACD al sinyali veriyor")
        elif macd_status == 'bearish':
            block.append("   ❌ MACD sat sinyali veriyor")

        block.append("")

        # Monte Carlo değerlendirme
        block.append("📌 Monte Carlo Projeksiyonu:")
        current = strategy['current_price']
        expected = mc_results['median_final_price']
        change_pct = ((expected - current) / current) * 100

        if change_pct > 10:
            block.append(f"   ✅ 1 yıllık beklenti olumlu (+{change_pct:.1f}%)")
        elif change_pct > 0:
            block.append(f"   ⚪ 1 yıllık beklenti hafif pozitif (+{change_pct:.1f}%)")
        else:
            block.append(f"   ⚠️  1 yıllık beklenti negatif ({change_pct:.1f}%)")

        block.append("")

        # Risk/Reward
        block.append("📌 Risk/Reward Değerlendirmesi:")
        rr = strategy['risk_reward_ratio']
        if rr >= 2.0:
            block.append(f"   ✅ İyi R:R oranı (1:{rr:.2f})")
        elif rr >= 1.5:
            block.append(f"   ⚪ Kabul edilebilir R:R oranı (1:{rr:.2f})")
        else:
            block.append(f"   ⚠️  Düşük R:R oranı (1:{rr:.2f})")

        block.append("")

        # Genel öneri
        block.append("💡 Genel Öneri:")

        bullish_count = sum([
            trend in ['strong_bullish', 'bullish'],
            rsi_status == 'oversold',
            macd_status == 'bullish',
            change_pct > 5,
            rr >= 1.5
        ])

        if bullish_count >= 4:
            block.append("   ✅ Güçlü alım fırsatı - Kademeli giriş stratejisi önerilir")
        elif bullish_count >= 3:
            block.append("   ⚪ Orta düzey fırsat - Dikkatli giriş yapılabilir")
        else:
            block.append("   ⚠️  Risk yüksek - Beklemek veya küçük pozisyon tercih edilmeli")

        block.append("")

        return "\n".join(block)

    def export_to_dict(
            self,
            asset_name: str,
            current_price: float,
            technical_analysis: Dict,
            monte_carlo_results: Dict,
            strategy: Dict
    ) -> Dict:
        """
        Raporu JSON formatında döndür
        """
        report_dict = {
            'metadata': {
                'asset': asset_name,
                'date': datetime.now().isoformat(),
                'current_price': current_price,
            },
            'technical_analysis': technical_analysis,
            'monte_carlo': monte_carlo_results,
            'strategy': strategy,
        }

        logger.info("Rapor dict formatına dönüştürüldü")
        return report_dict