import os
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from handlers.daily import daily_handler
from handlers.summary import summary_handler
from handlers.check import check_handler
from handlers.analysis import analysis_handler
from handlers.wallet import creat_handler, import_handler, info_handler, wallet_conversation_handler, buy_conversation_handler
from handlers.buttons import button_callback_handler


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def set_bot_commands(app):
    commands = [
        BotCommand("start", "Show welcome message"),
        BotCommand("daily", "Top trending tokens"),
        BotCommand("summary", "AI summary for a daily token"),
        BotCommand("check", "Check a token's metrics and analysis"),
        BotCommand("buy", "Buy a token"),
        BotCommand("creat", "Create a new wallet"),
        BotCommand("import", "Import an existing wallet"),
        BotCommand("info", "Show your wallet's ETH balance and Zora Coin holdings"),
        BotCommand("analysis", "In-depth AI analysis for a token"),
        BotCommand("delete", "Delete your wallet")
    ]
    await app.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 <b>Welcome to ZoraPulseBot!</b>\n\n"
        "I provide on-chain & market metrics for Zora coins, plus AI-powered analysis.\n\n"
        "<b>Available commands:</b>\n"
        "🔹 <b>/start</b> — Show welcome message\n"
        "🔹 <b>/daily</b> — Show top 5 coins' 24h metrics\n"
        "🔹 <b>/summary &lt;number&gt;</b> — AI summary for a daily token\n"
        "🔹 <b>/check &lt;contract&gt;</b> — Check a token's metrics and analysis\n"
        "🔹 <b>/buy &lt;contract&gt;</b> — Buy a token\n"
        "🔹 <b>/creat</b> — Create a new wallet\n"
        "🔹 <b>/import &lt;private_key&gt;</b> — Import an existing wallet\n"
        "🔹 <b>/info</b> — Show your wallet's ETH balance and Zora Coin holdings\n"
        "🔹 <b>/analysis &lt;contract&gt;</b> — In-depth AI analysis for a token\n"
        "🔹 <b>/delete</b> — Delete your wallet\n\n"
        "Type a command or use the menu below to get started!"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")


async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[DEBUG] ANY MESSAGE: {update}")


app = ApplicationBuilder().token(BOT_TOKEN).post_init(set_bot_commands).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("daily", daily_handler))
app.add_handler(CommandHandler("summary", summary_handler))
app.add_handler(CommandHandler("check", check_handler))
app.add_handler(CommandHandler("analysis", analysis_handler))
app.add_handler(CommandHandler("creat", creat_handler))
app.add_handler(CommandHandler("import", import_handler))
app.add_handler(CommandHandler("info", info_handler))
app.add_handler(wallet_conversation_handler)
app.add_handler(buy_conversation_handler)
app.add_handler(CallbackQueryHandler(button_callback_handler, pattern=r"^(summary|buy|analysis)_.*$"))
app.add_handler(MessageHandler(filters.ALL, debug_handler))


if __name__ == '__main__':
    print("bot started")
    app.run_polling()
