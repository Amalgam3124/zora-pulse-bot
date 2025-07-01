import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
FERNET_KEY = os.getenv('FERNET_KEY')

if not FERNET_KEY:
    raise ValueError('FERNET_KEY not set in .env')

fernet = Fernet(FERNET_KEY.encode())

def encrypt(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode() 