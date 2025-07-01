# handlers/daily.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils.zora import get_pulse_metrics
from handlers.summary import summary_handler

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
        address = m.get('contract', 'N/A')
        volume = m.get('volume_24h', 'N/A')
        cap = m.get('market_cap', 'N/A')
        delta = m.get('market_cap_delta_24h', 'N/A')
        holders = m.get('unique_holders', 'N/A')

        messages.append(
            f"{idx}. <b>{symbol}</b>\n"
            f"🔸 Address: <code>{address}</code>\n"  # Show token address under the name
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
    # Add five summary buttons in 2-2-1 layout
    keyboard = [
        [
            InlineKeyboardButton("AI summary for 1", callback_data="summary_1"),
            InlineKeyboardButton("AI summary for 2", callback_data="summary_2")
        ],
        [
            InlineKeyboardButton("AI summary for 3", callback_data="summary_3"),
            InlineKeyboardButton("AI summary for 4", callback_data="summary_4")
        ],
        [
            InlineKeyboardButton("AI summary for 5", callback_data="summary_5")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)

