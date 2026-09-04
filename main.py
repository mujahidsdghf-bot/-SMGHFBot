import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SYMBOL = "BTC-USD"
df = yf.download(SYMBOL, period="200d", interval="1d", auto_adjust=True)

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

signal_msg = "BUY SIGNAL 🟢" if (c1 and c2 and c3 and c4) else "WAIT / HOLD 🟡"
text = f"🤖 Daily Trading Bot Alert\n\nAsset: {SYMBOL}\nPrice: ${last['Close']:.2f}\nRSI: {last['RSI']:.2f}\nStatus: {signal_msg}"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
res = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
print("Alert Sent!" if res.status_code == 200 else f"Error: {res.text}")
