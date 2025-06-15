# utils/ai.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

MODELS = [
    "deepseek/deepseek-chat-v3-0324:free",
    "deepseek/deepseek-r1-0528:free"
    "google/gemini-2.0-flash-exp:free",
]

if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ OPENROUTER_API_KEY not found in environment variables")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

def ask_gpt(prompt: str) -> str:
    url = f"{OPENROUTER_API_BASE}/chat/completions"
    system_msg = {"role": "system", "content": "You are a crypto market analyst writing concise daily summaries."}
    user_msg = {"role": "user", "content": prompt}

    for model in MODELS:
        payload = {
            "model": model,
            "messages": [system_msg, user_msg],
            "max_tokens": 256,
            "temperature": 0.7
        }
        response = requests.post(url, headers=HEADERS, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            code = response.status_code
            if code in (401, 402, 429):
                continue
            else:
                raise
        data = response.json()
        choices = data.get("choices") or []
        if choices:
            content = choices[0].get("message", {}).get("content", "").strip()
            if content:
                return content
    return "No summary available."
