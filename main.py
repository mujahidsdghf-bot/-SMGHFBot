import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# అన్ని రకాల అసెట్స్ లిస్ట్
ASSETS = {
    # 1. ఇండియన్ మార్కెట్ ఇండెక్స్
    "^NSEI": "Nifty 50 🇮🇳",
    
    # 2. ప్రధాన క్రిప్టో
    "BTC-USD": "Bitcoin 🪙",
    "ETH-USD": "Ethereum 🪙",
    
    # 3. క్రిప్టో పెన్నీ కాయిన్స్
    "DOGE-USD": "Dogecoin (Penny) 🐕",
    "SHIB-USD": "Shiba Inu (Penny) 🐶",
    "ADA-USD": "Cardano (Penny) 🪙",
    
    # 4. ప్రధాన భారతీయ షేర్లు
    "RELIANCE.NS": "Reliance 🏢",
    "TATAMOTORS.NS": "Tata Motors 🚗",
    
    # 5. భారతీయ పెన్నీ షేర్లు (NSE)
    "IDEA.NS": "Vodafone Idea (Penny) 📱",
    "SUZLON.NS": "Suzlon Energy (Penny) ⚡",
    "YESBANK.NS": "Yes Bank (Penny) 🏦"
}

def analyze_asset(symbol):
    try:
        df = yf.download(symbol, period="200d", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 50:
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # EMA లెక్కింపు
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

        # RSI లెక్కింపు
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD లెక్కింపు
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
        
        # అతి తక్కువ ధర ఉండే పెన్నీ కాయిన్ల కోసం డెసిమల్స్
        price_format = f"{last['Close']:.6f}" if last['Close'] < 0.01 else f"{last['Close']:.2f}"

        return {
            "price_str": price_format,
            "rsi": last['RSI'],
            "signal": signal
        }
    except Exception:
        return None

message_lines = ["📊 **డైలీ మార్కెట్ సిగ్నల్స్ రిపోర్ట్**\n"]

for symbol, name in ASSETS.items():
    data = analyze_asset(symbol)
    if data:
        currency = "$" if "USD" in symbol else "₹"
        message_lines.append(
            f"🔹 **{name}**\n"
            f"ధర: {currency}{data['price_str']} | RSI: {data['rsi']:.1f}\n"
            f"సిగ్నల్: {data['signal']}\n"
        )

text = "\n".join(message_lines)

# టెలిగ్రామ్‌కు మెసేజ్ పంపడం
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
print("Alert Sent!" if res.status_code == 200 else f"Error: {res.text}")
