import os
import subprocess
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from web3 import Web3
from utils.db import init_db, save_wallet, get_wallet
from utils.crypto import encrypt, decrypt

ZORA_RPC = 'https://rpc.zora.energy'

# Initialize database
init_db()

# State for delete confirmation
AWAITING_DELETE_CONFIRM = range(1)

def delete_wallet(telegram_user_id: int):
    import sqlite3
    conn = sqlite3.connect('wallets.db')
    c = conn.cursor()
    c.execute('DELETE FROM wallets WHERE telegram_user_id = ?', (telegram_user_id,))
    conn.commit()
    conn.close()

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

# Handler registration helper for bot.py
wallet_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('delete', delete_handler)],
    states={
        AWAITING_DELETE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete_handler)]
    },
    fallbacks=[],
) 