# handlers/analysis.py
from telegram import Update
from telegram.ext import ContextTypes
from utils.zora import get_coin_metrics
from utils.ai import ask_gpt

async def analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_data = context.user_data

    if args:
        address = args[0]
        user_data['last_address'] = address
    else:
        address = user_data.get('last_address')

    if not address:
        await update.message.reply_text(
            "❌ Please provide a contract address, e.g. /analysis 0x1234..."
        )
        return


    metrics = get_coin_metrics(address)
    if not metrics:
        await update.message.reply_text(
            f"❌ Could not fetch metrics for address {address}. Please check and try again."
        )
        return

    symbol = metrics.get('symbol', 'N/A')
    volume = metrics.get('volume_24h', 'N/A')
    cap    = metrics.get('market_cap', 'N/A')
    delta  = metrics.get('market_cap_delta_24h', 'N/A')
    holders= metrics.get('unique_holders', 'N/A')

    summary_text = (
        f"**{symbol}** ({address})\n"
        f"- 24h Volume: {volume}\n"
        f"- Market Cap: {cap}\n"
        f"- ΔMarket Cap 24h: {delta}\n"
        f"- Holders: {holders}\n"
    )

    prompt = (
        "You are a crypto analyst. Based only on the following metrics, "
        "write **one concise paragraph** (2–3 sentences) highlighting the key takeaways "
        f"for {symbol}:\n\n"
        f"{summary_text}\n"
        "Focus on the most important insight; do not provide lists or bullet points."
    )

    try:
        analysis = ask_gpt(prompt)
    except Exception as e:
        await update.message.reply_text(f"❌ AI analysis failed: {e}")
        return

    await update.message.reply_text(analysis)