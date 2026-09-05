import os
import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np

# Secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()
UPSTOX_TOKEN = os.environ.get("UPSTOX_ACCESS_TOKEN", "").strip()

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram Credentials Missing!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- UPSTOX API కనెక్షన్ టెస్ట్ & లైవ్ ఫీడ్ ---
def get_upstox_live_status():
    if not UPSTOX_TOKEN:
        return "⚠️ Upstox Token సెట్ చేయలేదు (Yahoo Finance బ్యాకప్ వాడుతోంది)."
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {UPSTOX_TOKEN}"
    }
    url = "https://api.upstox.com/v2/user/profile"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json().get("data", {})
            user_name = data.get("user_name", "Trader")
            return f"✅ **Upstox API లైవ్ కనెక్ట్ అయింది!**\nయూజర్: {user_name} | బ్రోకర్: Active 🟢"
        else:
            return f"⚠️ Upstox API కనెక్షన్ ఎర్రర్: {res.status_code} (టోకెన్ ఎక్స్‌పైర్ అయ్యి ఉండవచ్చు)."
    except Exception as e:
        return f"⚠️ Upstox కనెక్షన్ ఫెయిల్ అయింది: {e}"

# --- మార్కెట్ అసెట్ లిస్ట్ ---
CATEGORIES = {
    "🎯 [ ఫ్యూచర్స్ స్పెషల్ (Index & F&O) ]": {
        "^NSEI": ("Nifty 50 Index", True),
        "RELIANCE.NS": ("Reliance Futures", True),
        "TCS.NS": ("TCS Futures", True),
        "HDFCBANK.NS": ("HDFC Bank Futures", True),
        "SBIN.NS": ("SBI Futures", True),
        "TATAMOTORS.NS": ("Tata Motors Futures", True),
        "BTC-USD": ("Bitcoin Futures", True),
        "ETH-USD": ("Ethereum Futures", True)
    },
    "🚗 [ EV & బ్యాటరీ స్టాక్స్ ]": {
        "TATAMOTORS.NS": ("Tata Motors (EV)", True),
        "M&M.NS": ("M&M (EV SUV)", True),
        "TVSMOTOR.NS": ("TVS Motor (EV 2W)", True),
        "OLECTRA.NS": ("Olectra (EV Bus)", False),
        "EXIDEIND.NS": ("Exide (Battery)", True),
        "ARE&M.NS": ("Amara Raja (Battery)", True),
        "SONACOMS.NS": ("Sona BLW", False),
        "TATACHEM.NS": ("Tata Chemicals", True)
    },
    "☀️ [ సోలార్ & రెన్యూవబుల్ స్టాక్స్ ]": {
        "TATAPOWER.NS": ("Tata Power (Solar)", True),
        "ADANIGREEN.NS": ("Adani Green", False),
        "NTPC.NS": ("NTPC Green", True),
        "SUZLON.NS": ("Suzlon Energy", False),
        "INOXGREEN.NS": ("Inox Green", False),
        "URJAGLOBAL.NS": ("Urja Global (Penny)", False),
        "ZODIAC.NS": ("Zodiac Energy", False)
    },
    "⚡ [ భారతీయ పెన్నీ షేర్లు ]": {
        "IDEA.NS": ("Vodafone Idea", False),
        "YESBANK.NS": ("Yes Bank", False),
        "RPOWER.NS": ("Reliance Power", False),
        "JPPOWER.NS": ("Jaiprakash Power", False),
        "SOUTHBANK.NS": ("South Indian Bank", False)
    },
    "🪙 [ టాప్ & గ్రీన్ క్రిప్టో ]": {
        "BTC-USD": ("Bitcoin", True),
        "ETH-USD": ("Ethereum", True),
        "SOL-USD": ("Solana", True),
        "DOGE-USD": ("Dogecoin (Penny)", True),
        "POWR-USD": ("Powerledger (Solar)", False),
        "ALGO-USD": ("Algorand (Green)", True)
    }
}

def analyze_market(symbol, has_futures):
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

        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - close.shift())
        low_close = np.abs(df['Low'] - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        
        last_price = close.iloc[-1]
        atr = atr if not np.isnan(atr) else (last_price * 0.02)

        c_buy = (ema9.iloc[-1] > ema21.iloc[-1]) and (rsi.iloc[-1] > 48)
        sig_intra = "BUY 🟢" if (c_buy and (last_price > ema9.iloc[-1])) else "HOLD 🟡"
        sig_swing = "BUY 🟢" if (c_buy and (last_price > ema50.iloc[-1])) else "HOLD 🟡"
        sig_long = "ACCUMULATE 🟢" if (last_price > ema50.iloc[-1]) else "HOLD / WAIT 🟡"

        tgt = last_price + (2.5 * atr)
        sl = max(0.000001, last_price - (1.5 * atr))

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

# రన్ చేయడం
upstox_status = get_upstox_live_status()
header_msg = f"🚀 **SM AI TRADING BOT (UPSTOX LIVE CONNECTED)**\n\n{upstox_status}"
send_telegram(header_msg)

for cat_name, items in CATEGORIES.items():
    lines = [f"{cat_name}\n======================="]
    for symbol, (name, has_fno) in items.items():
        data = analyze_market(symbol, has_fno)
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

print("All Reports Sent with Upstox Integration!")
