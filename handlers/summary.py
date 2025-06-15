# handlers/summary.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.zora import get_pulse_metrics
from utils.ai import ask_gpt

async def summary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].isdigit():
        return await update.message.reply_text(
            "Usage: /summary <1-5> (e.g., /summary 2)"
        )
    index = int(args[0])

    # Fetch metrics
    metrics = get_pulse_metrics()
    if not metrics:
        return await update.message.reply_text(
            "❌ Failed to fetch Zora Pulse metrics. Cannot generate analysis."
        )

    # Validate index
    if index < 1 or index > len(metrics):
        return await update.message.reply_text(
            f"❌ Invalid number. Please choose a number between 1 and {len(metrics)}."
        )

    # Select the specific coin metrics
    m = metrics[index - 1]
    data_text = (
        f"{m['symbol']}: Volume(24h)={m['volume_24h']}, "
        f"MarketCap={m['market_cap']}, "
        f"ΔMarketCap(24h)={m['market_cap_delta_24h']}, "
        f"Holders={m['unique_holders']}"
    )

    # Prepare prompt for AI
    prompt = (
        "You are a professional crypto market analyst.\n"
        f"Here are today's Zora Pulse Metrics for {m['symbol']}:\n"
        f"{data_text}\n\n"
        "Provide a concise and insightful analysis in plain text. "
        "Do not use any markup or formatting."
    )

    try:
        analysis = ask_gpt(prompt)
    except Exception as e:
        return await update.message.reply_text(f"❌ AI analysis failed: {e}")

    await update.message.reply_text(analysis.strip())