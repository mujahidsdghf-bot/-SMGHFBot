import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

ASSETS = {
    "^NSEI": "Nifty 50",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "DOGE-USD": "Dogecoin (Penny)",
    "SHIB-USD": "Shiba Inu (Penny)",
    "ADA-USD": "Cardano (Penny)",
    "RELIANCE.NS": "Reliance",
    "TATAMOTORS.NS": "Tata Motors",
    "IDEA.NS": "Vodafone Idea (Penny)",
    "SUZLON.NS": "Suzlon Energy (Penny)",
    "YESBANK.NS": "Yes Bank (Penny)"
}

def analyze_asset(symbol):
    try:
        df = yf.download(symbol, period="200d", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 50:
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

message_lines = ["📊 DAILY MARKET SIGNALS\n"]

for symbol, name in ASSETS.items():
    data = analyze_asset(symbol)
    if data:
        curr = "$" if "USD" in symbol else "Rs."
        message_lines.append(f"{name}:\nధర: {curr} {data['price']} | RSI: {data['rsi']}\nసిగ్నల్: {data['signal']}\n")

final_text = "\n".join(message_lines)

# ఫార్మాటింగ్ ఎర్రర్స్ లేకుండా సాధారణ టెక్స్ట్‌గా పంపడం
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
res = requests.post(url, data={"chat_id": CHAT_ID, "text": final_text})

if res.status_code == 200:
    print("Alert Sent Successfully!")
else:
    print(f"Telegram API Error: {res.status_code} - {res.text}")
    raise Exception(f"Failed to send alert: {res.text}")
