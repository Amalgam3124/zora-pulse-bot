# handlers/check.py
from telegram import Update
from telegram.ext import ContextTypes
from utils.zora import get_coin_metrics

async def check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: /check <contract_address>\n"
            "Example: /check 0x1234abcd..."
        )
        return

    address = args[0]
    metrics = get_coin_metrics(address)
    if not metrics:
        await update.message.reply_text(
            f"❌ Could not fetch metrics for address {address}. Please check the address and try again."
        )
        return

    symbol = metrics.get('symbol', 'N/A')
    volume = metrics.get('volume_24h', 'N/A')
    cap = metrics.get('market_cap', 'N/A')
    delta = metrics.get('market_cap_delta_24h', 'N/A')
    holders = metrics.get('unique_holders', 'N/A')

    text = (
        f"<b>{symbol}</b> ({address})\n"
        f"🔸 Volume (24h): {volume}\n"
        f"🔸 Market Cap: {cap}\n"
        f"🔸 ΔMarket Cap (24h): {delta}\n"
        f"🔸 Holders: {holders}\n"
    )

    await update.message.reply_text(text, parse_mode="HTML")
