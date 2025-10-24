"""
Ana uygulama entry point
"""
import sys
from datetime import datetime, timedelta

from utils.logger import logger
from config.settings import DATA_CONFIG

# Data
from data.data_collector import DataCollector
from data.historical_data import HistoricalData

# Analysis
from analysis.statistical_engine import StatisticalEngine
from analysis.technical_analyzer import TechnicalAnalyzer
from analysis.monte_carlo_simulator import MonteCarloSimulator
from analysis.scenario_generator import ScenarioGenerator
from analysis.gold_silver_ratio import GoldSilverRatio

# Strategy
from strategy.support_resistance import SupportResistance
from strategy.position_manager import PositionManager
from strategy.risk_calculator import RiskCalculator
from strategy.portfolio_optimizer import PortfolioOptimizer

# Backtest
from backtest.backtest_engine import BacktestEngine
from backtest.performance_metrics import PerformanceMetrics

# Output
from output.report_generator import ReportGenerator
from output.chart_generator import ChartGenerator
from output.export_manager import ExportManager
from output.telegram_sender import TelegramSender

# NLP
from nlp.command_parser import CommandParser, CommandExamples
from nlp.intent_classifier import IntentClassifier


class FinancialMetalAnalysis:
    """
    Ana uygulama sınıfı
    """

    def __init__(self):
        """
        Uygulama başlatıcı
        """
        logger.info("=" * 70)
        logger.info("🚀 FINANCIAL METAL ANALYSIS SYSTEM BAŞLATILIYOR")
        logger.info("=" * 70)

        # Modülleri başlat
        self.data_collector = DataCollector()
        self.technical_analyzer = TechnicalAnalyzer()
        self.mc_simulator = MonteCarloSimulator()
        self.scenario_gen = ScenarioGenerator()
        self.sr = SupportResistance()
        self.position_manager = PositionManager()
        self.risk_calc = RiskCalculator()

        self.report_gen = ReportGenerator()
        self.chart_gen = ChartGenerator()
        self.export_manager = ExportManager()
        self.telegram = TelegramSender()

        self.command_parser = CommandParser()
        self.intent_classifier = IntentClassifier()

        logger.info("✅ Tüm modüller başlatıldı")

    def run_full_analysis(
            self,
            asset_name: str = 'silver',
            target_price: float = None,
            send_telegram: bool = True,
            projection_days: int = None
    ):
        """
        Tam analiz çalıştır (5 blok)

        Args:
            asset_name: 'silver' veya 'gold'
            target_price: Hedef fiyat (opsiyonel)
            send_telegram: Telegram'a gönder mi
        """
        logger.info(f"TAM ANALİZ BAŞLIYOR: {asset_name.upper()}")

        # 1. VERİ TOPLAMA
        print("\n📊 Veri çekiliyor...")
        data = self.data_collector.fetch_price_data(asset_name, period='2y')

        if data is None:
            logger.error("Veri çekilemedi!")
            return

        # 2. TEKNİK ANALİZ
        print("📈 Teknik analiz yapılıyor...")
        tech = self.technical_analyzer.get_full_technical_analysis(data)

        # 3. DESTEK/DİRENÇ
        print("🎯 Destek/Direnç seviyeleri tespit ediliyor...")
        levels = self.sr.find_support_resistance_levels(data)
        levels_with_strength = self.sr.get_key_levels_with_strength(data)

        # Teknik analiz sonuçlarına ekle
        tech['support_levels'] = levels_with_strength['support_levels']
        tech['resistance_levels'] = levels_with_strength['resistance_levels']

        # 4. MONTE CARLO
        print("🎲 Monte Carlo simülasyonu çalışıyor...")
        mc_results = self.mc_simulator.run_full_analysis(
            data=data,
            target_price=target_price,
            custom_days=projection_days
        )

        # 5. STRATEJİ
        print("📋 Strateji oluşturuluyor...")
        strategy = self.position_manager.create_entry_strategy(
            support_levels=levels['support'],
            resistance_levels=levels['resistance'],
            current_price=tech['current_price'],
            atr=tech['atr']['value']
        )

        # 6. SENARYO ANALİZİ
        print("📊 Senaryolar oluşturuluyor...")
        scenarios = self.scenario_gen.generate_scenarios(data)

        # 7. RAPOR OLUŞTUR
        print("\n📄 Rapor oluşturuluyor...")
        report = self.report_gen.generate_full_report(
            asset_name=asset_name,
            current_price=tech['current_price'],
            technical_analysis=tech,
            monte_carlo_results=mc_results,
            strategy=strategy,
            scenarios=scenarios
        )

        # Raporu yazdır
        print("\n" + report)

        # 8. GRAFİKLER
        print("\n📊 Grafikler oluşturuluyor...")
        chart_paths = []

        # Fiyat grafiği
        price_chart = self.chart_gen.create_price_chart(
            data=tech['data_with_indicators'],
            technical_indicators=tech,
            filename=f'{asset_name}_price_chart.png'
        )
        chart_paths.append(price_chart)

        # Monte Carlo grafiği
        mc_chart = self.chart_gen.create_monte_carlo_chart(
            price_paths=mc_results['price_paths'],
            current_price=tech['current_price'],
            percentiles=mc_results,
            filename=f'{asset_name}_monte_carlo.png'
        )
        chart_paths.append(mc_chart)

        # Dağılım grafiği
        dist_chart = self.chart_gen.create_distribution_chart(
            final_prices=mc_results['price_paths'][:, -1],
            current_price=tech['current_price'],
            filename=f'{asset_name}_distribution.png'
        )
        chart_paths.append(dist_chart)

        print(f"✅ Grafikler kaydedildi: {len(chart_paths)} dosya")

        # 9. EXPORT
        print("\n💾 Raporlar export ediliyor...")

        # JSON export
        report_dict = self.report_gen.export_to_dict(
            asset_name=asset_name,
            current_price=tech['current_price'],
            technical_analysis=tech,
            monte_carlo_results=mc_results,
            strategy=strategy
        )
        json_path = self.export_manager.export_to_json(
            report_dict,
            filename=f'{asset_name}_report_{datetime.now().strftime("%Y%m%d")}.json'
        )
        print(f"✅ JSON: {json_path}")

        print("\n" + "=" * 70)
        print("🔍 TELEGRAM DEBUG")
        print("=" * 70)
        print(f"send_telegram parametresi: {send_telegram}")
        print(f"telegram.enabled: {self.telegram.enabled}")
        print(f"telegram.bot_token var mı: {bool(self.telegram.bot_token)}")
        print(f"telegram.chat_id var mı: {bool(self.telegram.chat_id)}")
        print("=" * 70)

        # 10. TELEGRAM
        if send_telegram and self.telegram.enabled:
            print("\n📱 Telegram'a gönderiliyor...")
            telegram_success = self.telegram.send_full_report(
                report_text=report,
                chart_paths=chart_paths
            )

            if telegram_success:
                print("✅ Telegram'a gönderildi!")
            else:
                print("❌ Telegram gönderilemedi")

        print("\n" + "=" * 70)
        print("✅ TAM ANALİZ TAMAMLANDI")
        print("=" * 70)

    def run_command(self, command: str, send_telegram: bool = True):
        """
        Doğal dil komutu çalıştır
        """
        logger.info(f"Komut alındı: {command}")

        # Komutu parse et
        parsed = self.command_parser.parse_command(command)

        asset = parsed['asset']
        analysis_type = parsed['analysis_type']
        target_price = parsed['target_price']
        time_period = parsed['time_period']  # ← GÜN SAYISI

        print(f"\n🎯 Asset: {asset.upper()}")
        print(f"📊 Analiz Tipi: {analysis_type}")

        if target_price:
            print(f"💰 Hedef Fiyat: ${target_price}")

        if time_period:  # ← YENİ
            print(f"⏰ Projeksiyon: {time_period} gün ({time_period // 252} yıl)")

        # Analiz tipine göre çalıştır
        if analysis_type == 'full_analysis':
            self.run_full_analysis(
                asset,
                target_price,
                send_telegram=send_telegram,
                projection_days=time_period  # ← EKLE
            )

        elif analysis_type == 'monte_carlo':
            self._run_monte_carlo_only(
                asset,
                target_price,
                projection_days=time_period,
                send_telegram=send_telegram # ← EKLE
            )

        elif analysis_type == 'technical':
            self._run_technical_only(asset)

        elif analysis_type == 'strategy':
            self._run_strategy_only(asset)

        elif analysis_type == 'backtest':
            self._run_backtest(asset)

        else:
            # Varsayılan: Tam analiz
            self.run_full_analysis(asset, target_price)

    def _run_monte_carlo_only(
            self,
            asset_name: str,
            target_price: float = None,
            projection_days: int = None,
            send_telegram: bool = False  # ← EKLE
    ):
        """Sadece Monte Carlo"""
        if projection_days is None:
            projection_days = 252

        data = self.data_collector.fetch_price_data(asset_name, period='2y')
        mc_results = self.mc_simulator.run_full_analysis(
            data,
            target_price=target_price,
            custom_days=projection_days
        )

        print("\n" + "=" * 70)
        print(f"🎲 MONTE CARLO SONUÇLARI - {asset_name.upper()}")
        print("=" * 70)
        print(f"⏰ Projeksiyon: {projection_days} gün ({projection_days // 252} yıl)")
        print(f"Medyan: ${mc_results['median_final_price']:.2f}")
        print(f"%5: ${mc_results['percentile_5']:.2f}")
        print(f"%95: ${mc_results['percentile_95']:.2f}")

        if target_price:
            print(f"\n🎯 Hedef ${target_price} olasılık: {mc_results['target_analysis']['probability']:.2%}")

        # TELEGRAM EKLE
        if send_telegram and self.telegram.enabled:
            print("\n📱 Telegram'a gönderiliyor...")

            # Basit metin raporu
            telegram_text = f"""
    🎲 MONTE CARLO SONUÇLARI - {asset_name.upper()}

    ⏰ Projeksiyon: {projection_days} gün ({projection_days // 252} yıl)

    📊 Sonuçlar:
      Medyan: ${mc_results['median_final_price']:.2f}
      %5: ${mc_results['percentile_5']:.2f}
      %95: ${mc_results['percentile_95']:.2f}

    ⚠️ Risk Metrikleri:
      VaR (5%): ${mc_results['risk_metrics']['var_5']:.2f}
      VaR (1%): ${mc_results['risk_metrics']['var_1']:.2f}
    """

            if target_price:
                telegram_text += f"\n🎯 Hedef ${target_price} olasılık: {mc_results['target_analysis']['probability']:.2%}"

            success = self.telegram.send_message(telegram_text)

            if success:
                print("✅ Telegram'a gönderildi!")
            else:
                print("❌ Telegram gönderilemedi")

    def _run_strategy_only(self, asset_name: str):
        """Sadece strateji"""
        data = self.data_collector.fetch_price_data(asset_name, period='2y')
        tech = self.technical_analyzer.get_full_technical_analysis(data)
        levels = self.sr.find_support_resistance_levels(data)

        strategy = self.position_manager.create_entry_strategy(
            support_levels=levels['support'],
            resistance_levels=levels['resistance'],
            current_price=tech['current_price'],
            atr=tech['atr']['value']
        )

        print("\n" + "=" * 70)
        print(f"📋 STRATEJİ - {asset_name.upper()}")
        print("=" * 70)

        for entry in strategy['entries']:
            print(f"Kademe {entry['level']}: ${entry['price']:.2f} (%{entry['size_pct']:.0f})")

        print(f"\nStop-Loss: ${strategy['stop_loss']:.2f}")
        print(f"Target: ${strategy['target']:.2f}")
        print(f"R/R: 1:{strategy['risk_reward_ratio']:.2f}")

    def _run_backtest(self, asset_name: str):
        """Backtest çalıştır"""
        print("\n🔄 Backtest çalışıyor...")

        # 3 yıllık veri
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3 * 365)

        data = self.data_collector.fetch_price_data(
            asset_name,
            start_date=start_date,
            end_date=end_date
        )

        engine = BacktestEngine()
        results = engine.run_backtest(data)

        metrics = PerformanceMetrics()
        all_metrics = metrics.get_all_metrics(results)

        print("\n" + "=" * 70)
        print(f"📊 BACKTEST SONUÇLARI - {asset_name.upper()}")
        print("=" * 70)
        print(f"Başlangıç: ${results['initial_capital']:.2f}")
        print(f"Final: ${results['final_capital']:.2f}")
        print(f"Getiri: {results['total_return_pct']:.2f}%")
        print(f"İşlem Sayısı: {results['total_trades']}")
        print(f"Kazanma Oranı: {results['win_rate']:.2%}")
        print(f"Sharpe Ratio: {all_metrics['sharpe_ratio']:.4f}")
        print(f"Max Drawdown: {all_metrics['max_drawdown_pct']:.2f}%")


def main():
    """
    Ana fonksiyon
    """
    print("=" * 70)
    print("🚀 FINANCIAL METAL ANALYSIS SYSTEM")
    print("=" * 70)

    # Uygulama başlat
    app = FinancialMetalAnalysis()

    # Komut satırı argümanları
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        app.run_command(command)
    else:
        # İnteraktif mod
        print("\n💡 Kullanım:")
        print("  python main.py <komut>")
        print("\nÖrnek:")
        print("  python main.py gümüş tam analiz")
        print("  python main.py silver monte carlo")
        print("  python main.py altın strateji\n")

        CommandExamples.print_examples()

        # Varsayılan: Silver tam analiz
        print("\n🎯 Varsayılan analiz çalışıyor: SILVER TAM ANALİZ\n")
        app.run_full_analysis('silver', send_telegram=True)


if __name__ == "__main__":
    main()