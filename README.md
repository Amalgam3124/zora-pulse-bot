# ZoraPulseBot

ZoraPulseBot is a Telegram bot that fetches on-chain and secondary-market metrics for Zora coins and provides AI-powered summaries and analyses.

## Features

- **/daily**  
  Shows the top 5 Zora coins by 24h trading volume with key metrics:
  - 24h Volume  
  - Market Cap  
  - ΔMarket Cap (24h)  
  - Unique Holders  
- **/check <contract>**  
  Fetches the same metrics for any Zora coin by its contract address.  
- **/summary <number>**  
  Provides a concise AI-generated summary for the Nth coin from the last `/daily`.  
- **/analysis [contract]**  
  Generates a brief AI-powered paragraph analysis for a given coin (uses last checked address if omitted).

## Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/Amalgam3124/zora-pulse-bot.git
   cd zora-pulse-bot
   ```

2. **Set up Python environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate     # macOS/Linux
   .\venv\Scripts\activate   # Windows PowerShell
   pip install -r requirements.txt
   ```

3. **Set up Node.js SDK**  
   ```bash
   cd zora-sdk
   npm install
   ```

4. **Configure environment variables**  
   Copy `.env.example` to `.env` and fill in:
   ```ini
   BOT_TOKEN=your_telegram_bot_token
   ZORA_API_KEY=your_zora_api_key
   OPENROUTER_API_KEY=sk-org-...
   OPENROUTER_API_BASE=https://openrouter.ai/api/v1
   ```

## Usage

Back in the project root:

```bash
python bot.py
```

Then in Telegram chat with your bot:

- `/start` – show welcome and commands  
- `/daily` – view top-5 pulse metrics  
- `/check 0x…` – view metrics for any coin  
- `/summary 1` – get concise summary for the 1st coin  
- `/analysis 0x…` – get a brief AI analysis for a coin  

## Project Structure

```
zora-pulse-bot/
├── bot.py
├── test.py
├── handlers/
│   ├── daily.py
│   ├── check.py
│   ├── summary.py
│   └── analysis.py
├── utils/
│   ├── zora.py
│   └── ai.py
├── zora-sdk/
│   ├── getPulseMetrics.js
│   ├── getCoinMetrics.js
│   ├── package.json
│   └── node_modules/
├── venv/
├── requirements.txt
├── .env.example
└── .gitignore
```

## License

MIT License. Feel free to use and adapt.
