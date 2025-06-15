# handlers/daily.py
from telegram import Update
from telegram.ext import ContextTypes
from utils.zora import get_pulse_metrics
async def daily_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    metrics = get_pulse_metrics()
    if not metrics:
        await update.message.reply_text(
            "❌ Failed to fetch Zora Pulse metrics. Please try again later."
        )
        return

    messages = ["🔥 <b>Zora Pulse Metrics (24h)</b> 🔥\n"]
    for idx, m in enumerate(metrics, start=1):
        symbol = m.get('symbol', 'N/A')
        volume = m.get('volume_24h', 'N/A')
        cap = m.get('market_cap', 'N/A')
        delta = m.get('market_cap_delta_24h', 'N/A')
        holders = m.get('unique_holders', 'N/A')

        messages.append(
            f"{idx}. <b>{symbol}</b>\n"
            f"🔸 Volume (24h): {volume}\n"
            f"🔸 Market Cap: {cap}\n"
            f"🔸 ΔMarket Cap (24h): {delta}\n"
            f"🔸 Holders: {holders}\n"
        )

    messages.append(
        "\nYou can use /summary followed by the coin number to get a detailed analysis for each coin.\n"
        "For example:\n"
        "• /summary 1 for the first coin\n"
        "• /summary 2 for the second coin\n"
        "… and so on."
    )

    text = "\n".join(messages)
    await update.message.reply_text(text, parse_mode="HTML")
