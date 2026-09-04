import os
import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

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
    "🇮🇳 [ నిఫ్టీ 50 ప్రధాన షేర్లు - గ్రూప్ 1 ]": {
        "RELIANCE.NS": ("Reliance", True), "TCS.NS": ("TCS", True), "HDFCBANK.NS": ("HDFC Bank", True),
        "BHARTIARTL.NS": ("Bharti Airtel", True), "ICICIBANK.NS": ("ICICI Bank", True), "INFY.NS": ("Infosys", True),
        "SBIN.NS": ("SBI", True), "ITC.NS": ("ITC", True), "HINDUNILVR.NS": ("HUL", True), "LT.NS": ("L&T", True),
        "BAJFINANCE.NS": ("Bajaj Finance", True), "HCLTECH.NS": ("HCL Tech", True), "MARUTI.NS": ("Maruti Suzuki", True),
        "SUNPHARMA.NS": ("Sun Pharma", True), "ADANIENT.NS": ("Adani Ent", True), "KOTAKBANK.NS": ("Kotak Bank", True),
        "TITAN.NS": ("Titan", True), "ONGC.NS": ("ONGC", True), "TATACONSUM.NS": ("Tata Consumer", True),
        "NTPC.NS": ("NTPC", True), "AXISBANK.NS": ("Axis Bank", True), "POWERGRID.NS": ("Power Grid", True),
        "BAJAJFINSV.NS": ("Bajaj Finserv", True), "M&M.NS": ("Mahindra & Mahindra", True), "COALINDIA.NS": ("Coal India", True)
    },
    "🇮🇳 [ నిఫ్టీ 50 ప్రధాన షేర్లు - గ్రూప్ 2 ]": {
        "JSWSTEEL.NS": ("JSW Steel", True), "TATASTEEL.NS": ("Tata Steel", True), "ADANIPORTS.NS": ("Adani Ports", True),
        "HINDALCO.NS": ("Hindalco", True), "GRASIM.NS": ("Grasim", True), "TECHM.NS": ("Tech Mahindra", True),
        "WIPRO.NS": ("Wipro", True), "ULTRACEMCO.NS": ("UltraTech Cement", True), "BRITANNIA.NS": ("Britannia", True),
        "NESTLEIND.NS": ("Nestle India", True), "ASIANPAINT.NS": ("Asian Paints", True), "BAJAJ-AUTO.NS": ("Bajaj Auto", True),
        "EICHERMOT.NS": ("Eicher Motors", True), "HEROMOTOCO.NS": ("Hero MotoCorp", True), "CIPLA.NS": ("Cipla", True),
        "DRREDDY.NS": ("Dr Reddy", True), "APOLLOHOSP.NS": ("Apollo Hospitals", True), "DIVISLAB.NS": ("Divis Lab", True),
        "BPCL.NS": ("BPCL", True), "SBILIFE.NS": ("SBI Life", True), "HDFCLIFE.NS": ("HDFC Life", True),
        "SHRIRAMFIN.NS": ("Shriram Finance", True), "BEL.NS": ("BEL", True), "TRENT.NS": ("Trent", True)
    },
    "🚗 [ EV & బ్యాటరీ స్టాక్స్ ]": {
        "TATAMOTORS.NS": ("Tata Motors (EV Leader)", True),
        "M&M.NS": ("M&M (EV SUV)", True),
        "TVSMOTOR.NS": ("TVS Motor (EV 2W)", True),
        "OLECTRA.NS": ("Olectra Greentech (EV Bus)", False),
        "EXIDEIND.NS": ("Exide Industries (Battery)", True),
        "ARE&M.NS": ("Amara Raja (Battery)", True),
        "SONACOMS.NS": ("Sona BLW (EV Parts)", False),
        "TATACHEM.NS": ("Tata Chemicals (Lithium)", True)
    },
    "☀️ [ సోలార్ & రెన్యూవబుల్ ఎనర్జీ స్టాక్స్ ]": {
        "TATAPOWER.NS": ("Tata Power (Solar/EV)", True),
        "ADANIGREEN.NS": ("Adani Green Energy", False),
        "NTPC.NS": ("NTPC Green", True),
        "SUZLON.NS": ("Suzlon Energy (Wind/Solar)", False),
        "INOXGREEN.NS": ("Inox Green Energy", False),
        "URJAGLOBAL.NS": ("Urja Global (Solar Penny)", False),
        "ZODIAC.NS": ("Zodiac Energy (Solar EPC)", False)
    },
    "⚡ [ భారతీయ పెన్నీ స్టాక్స్ ]": {
        "IDEA.NS": ("Vodafone Idea", False),
        "YESBANK.NS": ("Yes Bank", False),
        "RPOWER.NS": ("Reliance Power", False),
        "JPPOWER.NS": ("Jaiprakash Power", False),
        "SOUTHBANK.NS": ("South Indian Bank", False),
        "UCOBANK.NS": ("UCO Bank", False),
        "IOB.NS": ("Indian Overseas Bank", False),
        "CENTRALBK.NS": ("Central Bank", False),
        "GTLINFRA.NS": ("GTL Infra", False),
        "HFCL.NS": ("HFCL", False),
        "VIKASECO.NS": ("Vikas Ecotech", False)
    },
    "🪙 [ టాప్ క్రిప్టో అసెట్స్ ]": {
        "BTC-USD": ("Bitcoin", True),
        "ETH-USD": ("Ethereum", True),
        "SOL-USD": ("Solana", True),
        "BNB-USD": ("BNB", True),
        "XRP-USD": ("XRP", True),
        "ADA-USD": ("Cardano", True),
        "AVAX-USD": ("Avalanche", True)
    },
    "🐕 [ క్రిప్టో పెన్నీ, మీమ్ & గ్రీన్ కాయిన్స్ ]": {
        "POWR-USD": ("Powerledger (Solar Token)", False),
        "ALGO-USD": ("Algorand (Green Crypto)", True),
        "HBAR-USD": ("Hedera (Eco Token)", True),
        "DOGE-USD": ("Dogecoin (Penny)", True),
        "SHIB-USD": ("Shiba Inu (Penny)", False),
        "PEPE-USD": ("Pepe (Penny)", False),
        "FLOKI-USD": ("Floki (Penny)", False),
        "BONK-USD": ("Bonk (Penny)", False),
        "GALA-USD": ("Gala (Penny)", False)
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

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

send_telegram("🚀 **AI ALL-IN-ONE MEGA SCANNER REPORT**\n(Nifty 50, Penny, EV, Solar, Crypto & Futures)")

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

print("Mega Scanner Alert Sent Successfully!")
