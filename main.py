import os
import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

CATEGORIES = {
    "🇮🇳 [ నిఫ్టీ 50 స్టాక్స్ - గ్రూప్ 1 ]": {
        "RELIANCE.NS": ("Reliance", True), "TCS.NS": ("TCS", True), "HDFCBANK.NS": ("HDFC Bank", True),
        "BHARTIARTL.NS": ("Airtel", True), "ICICIBANK.NS": ("ICICI Bank", True), "INFY.NS": ("Infosys", True),
        "SBIN.NS": ("SBI", True), "ITC.NS": ("ITC", True), "HINDUNILVR.NS": ("HUL", True), "LT.NS": ("L&T", True),
        "BAJFINANCE.NS": ("Bajaj Fin", True), "HCLTECH.NS": ("HCL Tech", True), "MARUTI.NS": ("Maruti", True),
        "SUNPHARMA.NS": ("Sun Pharma", True), "ADANIENT.NS": ("Adani Ent", True), "KOTAKBANK.NS": ("Kotak", True),
        "TITAN.NS": ("Titan", True), "ONGC.NS": ("ONGC", True), "TATACONSUM.NS": ("Tata Cons", True),
        "NTPC.NS": ("NTPC", True), "AXISBANK.NS": ("Axis Bank", True), "POWERGRID.NS": ("Power Grid", True),
        "BAJAJFINSV.NS": ("Bajaj Finsv", True), "M&M.NS": ("M&M", True), "COALINDIA.NS": ("Coal India", True)
    },
    "🇮🇳 [ నిఫ్టీ 50 స్టాక్స్ - గ్రూప్ 2 ]": {
        "JSWSTEEL.NS": ("JSW Steel", True), "TATASTEEL.NS": ("Tata Steel", True), "ADANIPORTS.NS": ("Adani Ports", True),
        "HINDALCO.NS": ("Hindalco", True), "GRASIM.NS": ("Grasim", True), "TECHM.NS": ("Tech M", True),
        "WIPRO.NS": ("Wipro", True), "ULTRACEMCO.NS": ("UltraTech", True), "BRITANNIA.NS": ("Britannia", True),
        "NESTLEIND.NS": ("Nestle", True), "ASIANPAINT.NS": ("Asian Paints", True), "BAJAJ-AUTO.NS": ("Bajaj Auto", True),
        "EICHERMOT.NS": ("Eicher Mot", True), "HEROMOTOCO.NS": ("Hero Moto", True), "CIPLA.NS": ("Cipla", True),
        "DRREDDY.NS": ("Dr Reddy", True), "APOLLOHOSP.NS": ("Apollo Hosp", True), "DIVISLAB.NS": ("Divis Lab", True),
        "BPCL.NS": ("BPCL", True), "SBILIFE.NS": ("SBI Life", True), "HDFCLIFE.NS": ("HDFC Life", True),
        "SHRIRAMFIN.NS": ("Shriram Fin", True), "BEL.NS": ("BEL", True), "TRENT.NS": ("Trent", True)
    },
    "⚡ [ భారతీయ పెన్నీ షేర్లు ]": {
        "IDEA.NS": ("Vodafone Idea", False), "SUZLON.NS": ("Suzlon Energy", False), "YESBANK.NS": ("Yes Bank", False),
        "RPOWER.NS": ("Reliance Power", False), "JPPOWER.NS": ("Jaiprakash Power", False), "SOUTHBANK.NS": ("South Indian Bank", False),
        "UCOBANK.NS": ("UCO Bank", False), "IOB.NS": ("Indian Overseas Bank", False), "CENTRALBK.NS": ("Central Bank", False),
        "GTLINFRA.NS": ("GTL Infra", False), "HFCL.NS": ("HFCL", False), "VIKASECO.NS": ("Vikas Ecotech", False)
    },
    "🪙 [ టాప్ క్రిప్టో అసెట్స్ ]": {
        "BTC-USD": ("Bitcoin", True), "ETH-USD": ("Ethereum", True), "SOL-USD": ("Solana", True),
        "BNB-USD": ("BNB", True), "XRP-USD": ("XRP", True), "ADA-USD": ("Cardano", True), "AVAX-USD": ("Avalanche", True)
    },
    "🐕 [ క్రిప్టో పెన్నీ / మీమ్ కాయిన్స్ ]": {
        "DOGE-USD": ("Dogecoin", True), "SHIB-USD": ("Shiba Inu", False), "PEPE-USD": ("Pepe", False),
        "FLOKI-USD": ("Floki", False), "BONK-USD": ("Bonk", False), "GALA-USD": ("Gala", False)
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

        # ATR లెక్కింపు
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - close.shift())
        low_close = np.abs(df['Low'] - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        
        last_price = close.iloc[-1]
        atr = atr if not np.isnan(atr) else (last_price * 0.02)

        # వాల్యూమ్ స్పైక్
        avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
        last_vol = df['Volume'].iloc[-1]
        vol_alert = " 🔥[Vol Spike]" if (avg_vol > 0 and last_vol > avg_vol * 1.5) else ""

        # 3 రకాల ట్రేడింగ్ సిగ్నల్స్
        c_buy = (ema9.iloc[-1] > ema21.iloc[-1]) and (rsi.iloc[-1] > 48) and (rsi.iloc[-1] < 70)
        sig_intraday = "BUY 🟢" if (c_buy and (last_price > ema9.iloc[-1])) else "HOLD 🟡"
        sig_swing = "BUY 🟢" if (c_buy and (last_price > ema50.iloc[-1])) else "HOLD 🟡"
        sig_long = "ACCUMULATE 🟢" if (last_price > ema50.iloc[-1]) else "HOLD / WAIT 🟡"

        tgt = last_price + (2.5 * atr)
        sl = max(0.000001, last_price - (1.5 * atr))

        # ఫ్యూచర్స్ ట్రేడింగ్ సిగ్నల్
        fut_line = ""
        if has_futures:
            if (ema9.iloc[-1] > ema21.iloc[-1]) and (macd.iloc[-1] > macd_sig.iloc[-1]) and (rsi.iloc[-1] > 50):
                fut_line = f"  🎯 Futures: LONG 🟢 | Tgt: {tgt:.2f} | SL: {sl:.2f}"
            elif (ema9.iloc[-1] < ema21.iloc[-1]) and (macd.iloc[-1] < macd_sig.iloc[-1]) and (rsi.iloc[-1] < 45):
                f_tgt_s = last_price - (2.5 * atr)
                f_sl_s = last_price + (1.5 * atr)
                fut_line = f"  🔻 Futures: SHORT 🔴 | Tgt: {f_tgt_s:.2f} | SL: {f_sl_s:.2f}"
            else:
                fut_line = "  ⚖️ Futures: SIDEWAYS 🟡"

        def fmt(v):
            return f"{v:.6f}" if v < 0.01 else f"{v:.2f}"

        return {
            "price": fmt(last_price),
            "target": fmt(tgt),
            "sl": fmt(sl),
            "rsi": f"{rsi.iloc[-1]:.1f}",
            "intra": sig_intraday,
            "swing": sig_swing,
            "long": sig_long,
            "fut_line": fut_line,
            "vol_alert": vol_alert,
            "is_swing_buy": sig_swing == "BUY 🟢"
        }
    except Exception:
        return None

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

send_telegram("🚀 **AI ULTIMATE TRADING BOT SCANNER**\n(Nifty 50, Penny, Crypto, 3 Trading Modes & Futures)")

daily_best_picks = []

for cat_name, items in CATEGORIES.items():
    lines = [f"{cat_name}\n======================="]
    for symbol, (name, has_fno) in items.items():
        data = analyze_full_market(symbol, has_fno)
        if data:
            curr = "$" if "USD" in symbol else "₹"
            block = (
                f"🔹 **{name}**{data['vol_alert']}\n"
                f"  ధర: {curr}{data['price']} | RSI: {data['rsi']}\n"
                f"  ⚡ Intraday: {data['intra']} | 🌊 Swing: {data['swing']} | 🏛️ Long: {data['long']}\n"
                f"  🎯 టార్గెట్: {curr}{data['target']} | 🛑 SL: {curr}{data['sl']}\n"
            )
            if data['fut_line']:
                block += f"{data['fut_line']}\n"
            lines.append(block)

            if data['is_swing_buy']:
                daily_best_picks.append(f"🟢 {name} ({curr}{data['price']})")

    send_telegram("\n".join(lines))
    time.sleep(1)

# ప్రత్యేక రికమండేషన్ల సమ్మరీ
if daily_best_picks:
    summary = "🎯 **ఈరోజు బెస్ట్ BUY రికమండేషన్లు:**\n" + "\n".join(daily_best_picks)
else:
    summary = "⚠️ **ఈరోజు బలమైన BUY సిగ్నల్స్ లేవు, మార్కెట్ రీట్రేస్‌మెంట్ చూసేవరకు వేచి చూడండి.**"

send_telegram(summary)
print("All Advanced Trading Signals Sent Successfully!")
