import os
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters, CallbackQueryHandler
from web3 import Web3
from utils.db import init_db, save_wallet, get_wallet
from utils.crypto import encrypt, decrypt

ZORA_RPC = 'https://rpc.zora.energy'

# Initialize database
init_db()

# State for delete confirmation
AWAITING_DELETE_CONFIRM = range(1)

BUY_AWAIT_AMOUNT, BUY_AWAIT_CONFIRM = range(2)

***REMOVED***
user_buy_context = {}

def delete_wallet(telegram_user_id: int):
    import sqlite3
    conn = sqlite3.connect('wallets.db')
    c = conn.cursor()
    c.execute('DELETE FROM wallets WHERE telegram_user_id = ?', (telegram_user_id,))
    conn.commit()
    conn.close()

def get_reply_func(update):
    async def reply(text, **kwargs):
        if getattr(update, 'message', None):
            return await update.message.reply_text(text, **kwargs)
        elif getattr(update, 'callback_query', None) and update.callback_query.message:
            return await update.callback_query.message.reply_text(text, **kwargs)
    return reply

async def creat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from eth_account import Account
    acct = Account.create()
    address = acct.address
    private_key = acct.key.hex()
    encrypted_pk = encrypt(private_key)
    save_wallet(update.effective_user.id, address, encrypted_pk)
    msg = (
        f"✅ Wallet created!\n"
        f"<b>Address:</b> <code>{address}</code>\n"
        f"<b>Private Key:</b> <code>{private_key}</code>\n\n"
        f"<b>IMPORTANT:</b> Keep your private key safe! Anyone with this key can access your funds. We do not store your private key in plain text and cannot recover it for you."
    )
    await update.message.reply_text(msg, parse_mode="HTML")

async def import_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a private key, e.g. /import <private_key>")
        return
    pk = context.args[0]
    from eth_account import Account
    try:
        acct = Account.from_key(pk)
    except Exception:
        await update.message.reply_text("❌ Invalid private key format.")
        return
    address = acct.address
    encrypted_pk = encrypt(pk)
    save_wallet(update.effective_user.id, address, encrypted_pk)
    msg = (
        f"✅ Wallet imported!\n"
        f"<b>Address:</b> <code>{address}</code>\n"
        f"<b>Private Key:</b> <code>{pk}</code>\n\n"
        f"<b>IMPORTANT:</b> Keep your private key safe! Anyone with this key can access your funds. We do not store your private key in plain text and cannot recover it for you."
    )
    await update.message.reply_text(msg, parse_mode="HTML")

async def info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    wallet = get_wallet(user_id)
    if not wallet:
        await update.message.reply_text("Please create or import a wallet first using /creat or /import.")
        return
    address = wallet['address']
    # Query ETH balance
    w3 = Web3(Web3.HTTPProvider(ZORA_RPC))
    try:
        eth_balance = w3.eth.get_balance(address)
        eth_balance = w3.from_wei(eth_balance, 'ether')
    except Exception as e:
        eth_balance = f'Failed to fetch: {e}'
    # Query Zora Coin holdings
    try:
        result = subprocess.run([
            'node', os.path.join('zora-sdk', 'getWalletHoldings.js'), address
        ], capture_output=True, text=True, timeout=20)
        if result.returncode == 0:
            holdings = result.stdout.strip()
        else:
            holdings = '[]'
    except Exception:
        holdings = '[]'
    import json
    try:
        coins = json.loads(holdings)
    except Exception:
        coins = []
    msg = f"<b>Wallet Address</b>: <code>{address}</code>\n<b>ETH Balance</b>: {eth_balance} ETH\n\n<b>Zora Coin Holdings</b>:\n"
    if coins:
        for c in coins:
            msg += f"{c['symbol']}: {c['balance']}\n"
    else:
        msg += "No Zora Coin holdings found."
    await update.message.reply_text(msg, parse_mode="HTML")

async def delete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Are you sure you want to delete your wallet? Type 'confirm' to delete your wallet. This action cannot be undone.")
    return AWAITING_DELETE_CONFIRM

async def confirm_delete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip().lower() == 'confirm':
        delete_wallet(update.effective_user.id)
        await update.message.reply_text("✅ Your wallet has been deleted.")
    else:
        await update.message.reply_text("Wallet deletion cancelled. If you want to delete, please type /delete again.")
    return ConversationHandler.END

async def buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, address=None):
    reply = get_reply_func(update)
    print(f"[DEBUG] update.message.text: {getattr(update, 'message', None) and update.message.text}")
    if address is None:
        args = context.args
        if not args:
            if getattr(update, 'message', None) and update.message.text:
                parts = update.message.text.strip().split()
                if len(parts) > 1:
                    args = [parts[1]]
        if args:
            address = args[0]
    print(f"[DEBUG] buy_handler address: {address}")
    if not address or len(address) != 42 or not address.startswith('0x'):
        await reply("Usage: /buy <Zora Coin contract address>")
        return BUY_AWAIT_AMOUNT
    coin_address = address
    user_id = update.effective_user.id
    user_buy_context[user_id] = {'coin_address': coin_address}
    await reply("Please enter the amount of ETH to spend (e.g. 0.01):")
    return BUY_AWAIT_AMOUNT

async def buy_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = get_reply_func(update)
    user_id = update.effective_user.id
    if user_id not in user_buy_context:
        await reply("Please start with /buy <address>.")
        return ConversationHandler.END
    try:
        eth_amount = float(update.message.text.strip())
        if eth_amount <= 0:
            raise ValueError
    except Exception:
        await reply("Please enter a valid positive ETH amount.")
        return BUY_AWAIT_AMOUNT
    user_buy_context[user_id]['eth_amount'] = str(eth_amount)
    coin_address = user_buy_context[user_id]['coin_address']
    keyboard = [
        [InlineKeyboardButton(f"Yes, buy {eth_amount} ETH of {coin_address[:6]}...{coin_address[-4:]}", callback_data='buy_confirm')],
        [InlineKeyboardButton("Cancel", callback_data='buy_cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await reply(
        f"Are you sure you want to buy {eth_amount} ETH of {coin_address}?",
        reply_markup=reply_markup
    )
    return BUY_AWAIT_CONFIRM

async def buy_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in user_buy_context:
        await query.edit_message_text("Session expired. Please start with /buy <address>.")
        return ConversationHandler.END
    if query.data == 'buy_cancel':
        await query.edit_message_text("Buy cancelled.")
        user_buy_context.pop(user_id, None)
        return ConversationHandler.END
    wallet = get_wallet(user_id)
    if not wallet:
        await query.edit_message_text("You have not created or imported a wallet. Please use /creat or /import first.")
        user_buy_context.pop(user_id, None)
        return ConversationHandler.END
    address = wallet['address']
    encrypted_pk = wallet['encrypted_private_key']
    w3 = Web3(Web3.HTTPProvider(ZORA_RPC))
    try:
        eth_balance = w3.eth.get_balance(address)
        eth_balance = w3.from_wei(eth_balance, 'ether')
    except Exception as e:
        await query.edit_message_text(f"Failed to fetch ETH balance: {e}")
        user_buy_context.pop(user_id, None)
        return ConversationHandler.END
    eth_amount = float(user_buy_context[user_id]['eth_amount'])
    if eth_balance < eth_amount:
        await query.edit_message_text(f"Insufficient ETH balance. Your balance: {eth_balance} ETH.")
        user_buy_context.pop(user_id, None)
        return ConversationHandler.END
    try:
        private_key = decrypt(encrypted_pk)
    except Exception:
        await query.edit_message_text("Failed to decrypt your private key.")
        user_buy_context.pop(user_id, None)
        return ConversationHandler.END
    coin_address = user_buy_context[user_id]['coin_address']
    import subprocess, sys
    try:
        result = subprocess.run([
            'node', os.path.join('zora-sdk', 'buyCoin.js'), private_key, coin_address, str(eth_amount)
        ], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            import json
            tx = json.loads(result.stdout.strip())
            await query.edit_message_text(f"✅ Buy order sent!\nTransaction hash: <code>{tx['hash']}</code>", parse_mode="HTML")
        else:
            await query.edit_message_text(f"Buy failed: {result.stderr}")
    except Exception as e:
        await query.edit_message_text(f"Buy failed: {e}")
    user_buy_context.pop(user_id, None)
    return ConversationHandler.END

# Handler registration helper for bot.py
wallet_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('delete', delete_handler)],
    states={
        AWAITING_DELETE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete_handler)]
    },
    fallbacks=[],
)

buy_conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler('buy', buy_handler),
        CallbackQueryHandler(buy_handler, pattern=r"^buy_0x[a-fA-F0-9]{40}$")
    ],
    states={
        BUY_AWAIT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_amount_handler)],
        BUY_AWAIT_CONFIRM: [CallbackQueryHandler(buy_confirm_handler)],
    },
    fallbacks=[],
    allow_reentry=True
) 