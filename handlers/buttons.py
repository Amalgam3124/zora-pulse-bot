from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from handlers.summary import summary_handler
from handlers.analysis import analysis_handler
from handlers.wallet import buy_handler

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("summary_"):
        idx = data.split("_", 1)[1]
        context.args = [idx]
        await summary_handler(update, context)
    elif data.startswith("buy_"):
        address = data.split("_", 1)[1]
        if address and address.startswith("0x") and len(address) == 42:
            await query.message.reply_text(
                f"/buy {address}",
                reply_markup={"force_reply": True}
            )
        else:
            await query.message.reply_text("Invalid contract address for buy.")
        return
    elif data.startswith("analysis_"):
        address = data.split("_", 1)[1]
        context.args = [address]
        await analysis_handler(update, context) 