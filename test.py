import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
MODEL = "deepseek/deepseek-r1-0528:free"

if not OPENROUTER_API_KEY:
    print("❌ OPENROUTER_API_KEY not found!")
    exit()

print(f"✅ API Key found: {OPENROUTER_API_KEY[:15]}...")
print(f"✅ Using model: {MODEL}")

def ask_hf(prompt):
    url = f"{OPENROUTER_API_BASE}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "DeepSeek Bot"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 256,
        "temperature": 0.7
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        
        result = r.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.HTTPError as e:
        if r.status_code == 401:
            raise ValueError("Invalid OpenRouter API key")
        elif r.status_code == 402:
            raise ValueError("No credits or model not available")
        elif r.status_code == 429:
            raise ValueError("Rate limit exceeded")
        else:
            raise e
    except Exception as e:
        raise Exception(f"API request failed: {e}")

def test_model():
    test_prompt = "Hello! How are you today?"
    
    try:
        response = ask_hf(test_prompt)
        print("✅ Model working!")
        print(f"📝 Test response: {response}")
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def interactive_test():
    print(f"🚀 Testing {MODEL}...\n")
    
    if test_model():
        print(f"\n🎉 Model {MODEL} is ready!")
        
        while True:
            user_input = input("\n💬 Enter your message (or 'quit' to exit): ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            try:
                response = ask_hf(user_input)
                print(f"🤖 DeepSeek: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    interactive_test()