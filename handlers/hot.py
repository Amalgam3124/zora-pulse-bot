from telegram import Update
from telegram.ext import ContextTypes
from utils.zora import get_coin_metrics
from utils.twitter import get_twitter_count

async def hot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: /hot <contract_address>\nExample: /hot 0x1234abcd..."
        )
        return

    address = args[0]
    metrics = get_coin_metrics(address)
    if not metrics:
        await update.message.reply_text(
            f"❌ Could not fetch metrics for address {address}. Please check the address and try again."
        )
        return

    symbol = metrics.get('symbol', None)
    if not symbol or symbol == 'N/A':
        await update.message.reply_text(f"❌ Could not find symbol for address {address}.")
        return

    wait_msg = await update.message.reply_text(f"🔍 Querying X (Twitter) for ${symbol} tweets in the past week...")
    try:
        count = get_twitter_count(symbol)
    except Exception as e:
        await wait_msg.edit_text(f"Error: {e}")
        return
    if count == -1:
        await wait_msg.edit_text(f"❌ Failed to fetch tweet count for ${symbol}.")
        return
    await wait_msg.edit_text(f"🔥 <b>{symbol}</b> ({address})\nX (Twitter) tweet count in the past week: <b>{count}</b>\nHotness is defined as the total number of tweets in the past week.", parse_mode="HTML") 