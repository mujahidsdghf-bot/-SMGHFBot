import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

# కేటగిరీల వారీగా విడదీసిన జాబితా
CATEGORIES = {
    "🇮🇳 [ నిఫ్టీ 50 టాప్ షేర్లు ]": {
        "^NSEI": "Nifty 50 (Index)",
        "RELIANCE.NS": "Reliance",
        "TCS.NS": "TCS",
        "HDFCBANK.NS": "HDFC Bank",
        "INFY.NS": "Infosys",
        "ICICIBANK.NS": "ICICI Bank",
        "SBIN.NS": "SBI",
        "ITC.NS": "ITC"
    },
    "⚡ [ భారతీయ పెన్నీ స్టాక్స్ ]": {
        "IDEA.NS": "Vodafone Idea",
        "SUZLON.NS": "Suzlon Energy",
        "YESBANK.NS": "Yes Bank",
        "SOUTHBANK.NS": "South Indian Bank",
        "UCOBANK.NS": "UCO Bank"
    },
    "🪙 [ టాప్ క్రిప్టో ]": {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "SOL-USD": "Solana"
    },
    "🐕 [ క్రిప్టో పెన్నీ కాయిన్స్ ]": {
        "DOGE-USD": "Dogecoin",
        "SHIB-USD": "Shiba Inu",
        "ADA-USD": "Cardano",
        "PEPE-USD": "Pepe"
    }
}

def analyze_asset(symbol):
    try:
        df = yf.download(symbol, period="200d", interval="1d", auto_adjust=True, progress=False)
        if df is None or df.empty or len(df) < 50:
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        last = df.iloc[-1]

        c1 = last['EMA_9'] > last['EMA_21']
        c2 = last['Close'] > last['EMA_50']
        c3 = (last['RSI'] > 45) and (last['RSI'] < 68)
        c4 = last['MACD'] > last['Signal_Line']

        signal = "BUY 🟢" if (c1 and c2 and c3 and c4) else "HOLD 🟡"
        price_val = f"{last['Close']:.6f}" if last['Close'] < 0.01 else f"{last['Close']:.2f}"

        return {
            "price": price_val,
            "rsi": f"{last['RSI']:.1f}",
            "signal": signal
        }
    except Exception:
        return None

message_lines = ["📊 DAILY MARKET SIGNALS REPORT\n=======================\n"]

for cat_name, assets in CATEGORIES.items():
    message_lines.append(f"\n{cat_name}")
    message_lines.append("-----------------------")
    for symbol, name in assets.items():
        data = analyze_asset(symbol)
        if data:
            curr = "$" if "USD" in symbol else "₹"
            message_lines.append(f"• {name}: {curr}{data['price']} | RSI: {data['rsi']} | {data['signal']}")

final_text = "\n".join(message_lines)

# టెలిగ్రామ్ మెసేజ్ పంపడం
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
res = requests.post(url, data={"chat_id": CHAT_ID, "text": final_text})

if res.status_code == 200:
    print("Alert Sent Successfully!")
else:
    print(f"Telegram Error: {res.status_code} - {res.text}")
    raise Exception(f"Failed to send alert: {res.text}")
