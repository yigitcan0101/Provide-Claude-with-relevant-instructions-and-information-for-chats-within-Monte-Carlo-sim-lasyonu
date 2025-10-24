"""
Çıktı export yöneticisi (JSON, CSV)
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List  # ← List de eklendi
from datetime import datetime

from utils.logger import logger
from config.settings import OUTPUT_CONFIG


class ExportManager:
    """
    Raporları farklı formatlarda export eder
    """

    def __init__(self):
        """
        ExportManager başlatıcı
        """
        self.reports_dir = OUTPUT_CONFIG['reports_dir']
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        logger.info("ExportManager başlatıldı")

    def export_to_json(
            self,
            data: Dict,
            filename: Optional[str] = None
    ) -> str:
        """
        JSON olarak export et

        Args:
            data: Export edilecek veri
            filename: Dosya adı (opsiyonel)

        Returns:
            str: Dosya yolu
        """
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"JSON export: {filepath}")
        return str(filepath)

    def export_to_csv(
            self,
            df: pd.DataFrame,
            filename: Optional[str] = None
    ) -> str:
        """
        CSV olarak export et

        Args:
            df: DataFrame
            filename: Dosya adı

        Returns:
            str: Dosya yolu
        """
        if filename is None:
            filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = self.reports_dir / filename
        df.to_csv(filepath, index=True)

        logger.info(f"CSV export: {filepath}")
        return str(filepath)

    def export_trades(
            self,
            trades: List[Dict],
            filename: Optional[str] = None
    ) -> str:
        """
        Trade listesini CSV olarak export et

        Args:
            trades: İşlem listesi
            filename: Dosya adı

        Returns:
            str: Dosya yolu
        """
        if filename is None:
            filename = f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        trades_df = pd.DataFrame(trades)
        return self.export_to_csv(trades_df, filename)