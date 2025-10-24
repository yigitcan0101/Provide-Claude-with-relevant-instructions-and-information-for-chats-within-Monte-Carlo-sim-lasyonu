"""
Telegram mesaj formatlaması
"""
from typing import Dict, List


def format_message_html(
        title: str,
        sections: List[Dict[str, str]]
) -> str:
    """
    HTML formatında Telegram mesajı oluştur

    Args:
        title: Başlık
        sections: [{'header': 'Başlık', 'content': 'İçerik'}, ...]

    Returns:
        str: HTML formatında mesaj
    """
    message = [f"<b>{title}</b>\n"]

    for section in sections:
        header = section.get('header', '')
        content = section.get('content', '')

        if header:
            message.append(f"\n<b>{header}</b>")

        if content:
            message.append(content)

    return "\n".join(message)


def format_price_message(
        asset_name: str,
        current_price: float,
        change_pct: float,
        trend: str
) -> str:
    """
    Fiyat bildirimi mesajı

    Args:
        asset_name: Asset adı
        current_price: Mevcut fiyat
        change_pct: Değişim yüzdesi
        trend: Trend

    Returns:
        str: Formatlanmış mesaj
    """
    emoji = "📈" if change_pct > 0 else "📉"

    message = f"""
<b>{emoji} {asset_name.upper()} Fiyat Bildirimi</b>

💰 Mevcut Fiyat: ${current_price:.2f}
📊 Değişim: {change_pct:+.2f}%
📈 Trend: {trend}
"""

    return message.strip()


def format_strategy_message(
        asset_name: str,
        strategy: Dict
) -> str:
    """
    Strateji önerisi mesajı

    Args:
        asset_name: Asset adı
        strategy: Strateji detayları

    Returns:
        str: Formatlanmış mesaj
    """
    message = [f"<b>🎯 {asset_name.upper()} Strateji Önerisi</b>\n"]

    message.append(f"💰 Mevcut Fiyat: ${strategy['current_price']:.2f}\n")

    message.append("<b>📈 Giriş Noktaları:</b>")
    for entry in strategy['entries']:
        message.append(f"  Kademe {entry['level']}: ${entry['price']:.2f} (%{entry['size_pct']:.0f})")

    message.append(f"\n🛑 Stop-Loss: ${strategy['stop_loss']:.2f}")
    message.append(f"🎯 Target: ${strategy['target']:.2f}")
    message.append(f"📊 R/R: 1:{strategy['risk_reward_ratio']:.2f}")

    if strategy.get('warning'):
        message.append(f"\n⚠️ {strategy['warning']}")

    return "\n".join(message)


def format_monte_carlo_message(
        asset_name: str,
        mc_results: Dict
) -> str:
    """
    Monte Carlo sonuçları mesajı

    Args:
        asset_name: Asset adı
        mc_results: Monte Carlo sonuçları

    Returns:
        str: Formatlanmış mesaj
    """
    message = [f"<b>🎲 {asset_name.upper()} Monte Carlo Sonuçları</b>\n"]

    message.append(f"📊 Projeksiyon: {mc_results['days']} gün")
    message.append(f"🔄 İterasyon: {mc_results['iterations']:,}\n")

    message.append("<b>💰 Beklenen Fiyat Aralığı:</b>")
    message.append(f"  Medyan: ${mc_results['median_final_price']:.2f}")
    message.append(f"  %5: ${mc_results['percentile_5']:.2f}")
    message.append(f"  %95: ${mc_results['percentile_95']:.2f}\n")

    if 'target_analysis' in mc_results and mc_results['target_analysis'].get('user_defined'):
        message.append("<b>🎯 Hedef Analizi:</b>")
        message.append(f"  Hedef: ${mc_results['target_analysis']['target_price']:.2f}")
        message.append(f"  Olasılık: {mc_results['target_analysis']['probability']:.1%}")

    return "\n".join(message)


def split_long_message(message: str, max_length: int = 4096) -> List[str]:
    """
    Uzun mesajı böl (Telegram 4096 karakter limiti)

    Args:
        message: Mesaj
        max_length: Maksimum uzunluk

    Returns:
        list: Bölünmüş mesajlar
    """
    if len(message) <= max_length:
        return [message]

    # Satırlara böl
    lines = message.split('\n')
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1  # +1 for newline

        if current_length + line_length > max_length:
            # Mevcut chunk'ı kaydet
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length

    # Son chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks


def escape_html(text: str) -> str:
    """
    HTML özel karakterlerini escape et

    Args:
        text: Metin

    Returns:
        str: Escape edilmiş metin
    """
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text