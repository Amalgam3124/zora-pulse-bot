import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from handlers.daily import daily_handler
from handlers.summary import summary_handler
from handlers.check import check_handler
from handlers.analysis import analysis_handler


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 <b>Welcome to ZoraPulseBot!</b>\n\n"
        "I provide on-chain & market metrics for Zora coins, plus AI-powered analysis.\n\n"
        "🔹 <b>/daily</b> — Show top 5 coins’ 24h metrics\n"
        "🔹 <b>/summary &lt;number&gt;</b> — Quick summary of the #th coin from /daily\n"
        "🔹 <b>/check &lt;contract&gt;</b> — Fetch metrics for any coin\n"
        "🔹 <b>/analysis [contract]</b> — In-depth AI analysis (uses last checked if omitted)\n\n"
        "Type a command to get started!"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")



app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("daily", daily_handler))
app.add_handler(CommandHandler("summary", summary_handler))
app.add_handler(CommandHandler("check", check_handler))
app.add_handler(CommandHandler("analysis", analysis_handler))



if __name__ == '__main__':
    app.run_polling()
