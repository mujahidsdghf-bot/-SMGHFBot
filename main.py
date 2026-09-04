import os
import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

CATEGORIES = {
    "🎯 [ ఫ్యూచర్స్ స్పెషల్ (F&O & Index) ]": {
        "^NSEI": ("Nifty 50 Index Futures", True),
        "RELIANCE.NS": ("Reliance Futures", True),
        "TCS.NS": ("TCS Futures", True),
        "HDFCBANK.NS": ("HDFC Bank Futures", True),
        "SBIN.NS": ("SBI Futures", True),
        "TATAMOTORS.NS": ("Tata Motors Futures", True),
        "BTC-USD": ("Bitcoin Futures", True),
        "ETH-USD": ("Ethereum Futures", True)
    },
    "🇮🇳 [ నిఫ్టీ 50 ఇతర ప్రధాన స్టాక్స్ ]": {
        "BHARTIARTL.NS": ("Airtel", True), "ICICIBANK.NS": ("ICICI Bank", True),
        "INFY.NS": ("Infosys", True), "ITC.NS": ("ITC", True),
        "LT.NS": ("L&T", True), "BAJFINANCE.NS": ("Bajaj Finance", True),
        "MARUTI.NS": ("Maruti", True), "SUNPHARMA.NS": ("Sun Pharma", True)
    },
    "⚡ [ భారతీయ పెన్నీ స్టాక్స్ (Cash Only) ]": {
        "IDEA.NS": ("Vodafone Idea", False),
        "SUZLON.NS": ("Suzlon Energy", False),
        "YESBANK.NS": ("Yes Bank", False),
        "RPOWER.NS": ("Reliance Power", False),
        "SOUTHBANK.NS": ("South Indian Bank", False)
    },
    "🪙 [ క్రిప్టో & పెన్నీ కాయిన్స్ ]": {
        "SOL-USD": ("Solana", True),
        "DOGE-USD": ("Dogecoin", True),
        "SHIB-USD": ("Shiba Inu", False),
        "PEPE-USD": ("Pepe", False)
    }
}

def analyze_full_market(symbol, has_futures):
    try:
        df = yf.download(symbol, period="100d", interval="1d", auto_adjust=True, progress=False)
        if df is None or df.empty or len(df) < 30:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df['Close']
        ema9 = close.ewm(span=9, adjust=False).mean()
        ema21 = close.ewm(span=21, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        macd_sig = macd.ewm(span=9, adjust=False).mean()

        # ATR
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - close.shift())
        low_close = np.abs(df['Low'] - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        
        last_price = close.iloc[-1]
        atr = atr if not np.isnan(atr) else (last_price * 0.02)

        # 3 రకాల ట్రేడింగ్ సిగ్నల్స్
        c_buy = (ema9.iloc[-1] > ema21.iloc[-1]) and (rsi.iloc[-1] > 48)
        sig_intra = "BUY 🟢" if (c_buy and (last_price > ema9.iloc[-1])) else "HOLD 🟡"
        sig_swing = "BUY 🟢" if (c_buy and (last_price > ema50.iloc[-1])) else "HOLD 🟡"
        sig_long = "ACCUMULATE 🟢" if (last_price > ema50.iloc[-1]) else "HOLD / WAIT 🟡"

        tgt = last_price + (2.5 * atr)
        sl = max(0.000001, last_price - (1.5 * atr))

        # ఫ్యూచర్స్ ట్రేడింగ్ సిగ్నల్ (తప్పనిసరిగా డిస్ప్లే అయ్యేలా)
        fut_line = ""
        if has_futures:
            if (ema9.iloc[-1] >= ema21.iloc[-1]) and (rsi.iloc[-1] >= 48):
                fut_line = f"  🔮 Futures: LONG 🟢 | Tgt: {tgt:.2f} | SL: {sl:.2f}"
            elif (ema9.iloc[-1] < ema21.iloc[-1]) and (rsi.iloc[-1] <= 52):
                f_tgt_s = last_price - (2.5 * atr)
                f_sl_s = last_price + (1.5 * atr)
                fut_line = f"  🔮 Futures: SHORT 🔴 | Tgt: {f_tgt_s:.2f} | SL: {f_sl_s:.2f}"
            else:
                fut_line = "  🔮 Futures: NEUTRAL / RANGEBOUND 🟡"

        def fmt(v):
            return f"{v:.6f}" if v < 0.01 else f"{v:.2f}"

        return {
            "price": fmt(last_price),
            "target": fmt(tgt),
            "sl": fmt(sl),
            "rsi": f"{rsi.iloc[-1]:.1f}",
            "intra": sig_intra,
            "swing": sig_swing,
            "long": sig_long,
            "fut_line": fut_line
        }
    except Exception:
        return None

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

send_telegram("🚀 **AI PRO MARKET REPORT**\n(Includes Futures LONG/SHORT & 3 Trading Modes)")

for cat_name, items in CATEGORIES.items():
    lines = [f"{cat_name}\n======================="]
    for symbol, (name, has_fno) in items.items():
        data = analyze_full_market(symbol, has_fno)
        if data:
            curr = "$" if "USD" in symbol else "₹"
            block = (
                f"🔹 **{name}**\n"
                f"  ధర: {curr}{data['price']} | RSI: {data['rsi']}\n"
                f"  ⚡ Intraday: {data['intra']} | 🌊 Swing: {data['swing']} | 🏛️ Long: {data['long']}\n"
                f"  🎯 Spot Target: {curr}{data['target']} | 🛑 SL: {curr}{data['sl']}\n"
            )
            if data['fut_line']:
                block += f"{data['fut_line']}\n"
            lines.append(block)

    send_telegram("\n".join(lines))
    time.sleep(1)

print("Report with explicit Futures Sent Successfully!")
