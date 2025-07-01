import sqlite3
from datetime import datetime

DB_PATH = 'wallets.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            telegram_user_id INTEGER PRIMARY KEY,
            address TEXT NOT NULL,
            encrypted_private_key TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_wallet(telegram_user_id: int, address: str, encrypted_private_key: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO wallets (telegram_user_id, address, encrypted_private_key, created_at)
        VALUES (?, ?, ?, ?)
    ''', (telegram_user_id, address, encrypted_private_key, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_wallet(telegram_user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT address, encrypted_private_key FROM wallets WHERE telegram_user_id = ?', (telegram_user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'address': row[0], 'encrypted_private_key': row[1]}
    return None 