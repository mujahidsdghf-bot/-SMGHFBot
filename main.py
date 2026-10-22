import os
import time
import requests
import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# SECRETS & CHAT IDs CONFIGURATION
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
UPSTOX_TOKEN = os.environ.get("UPSTOX_ACCESS_TOKEN", "").strip()

FREE_CHAT_ID = os.environ.get("FREE_CHAT_ID", "-1004438599671").strip()
VIP_CHAT_ID = os.environ.get("VIP_CHAT_ID", "-1004446963554").strip()

def send_telegram(text, chat_id=FREE_CHAT_ID):
    if not BOT_TOKEN or not chat_id:
        print("Telegram Credentials or Chat ID Missing!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
        if response.status_code != 200:
            print(f"Telegram Send Error: {response.text}")
    except Exception as e:
        print(f"Telegram Error: {e}")

# ==========================================
# UPSTOX OPTION CHAIN DATA CHECKER
# ==========================================
def check_option_chain_data():
    if not UPSTOX_TOKEN:
        print("Upstox Token Missing!")
        return
        
    url = "https://api.upstox.com/v2/market-quote/quotes?instrument_key=NSE_INDEX|Nifty 50"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {UPSTOX_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code == 200 and data.get("status") == "success":
            msg = (
                "📊 *Upstox Option Market Update*\n"
                "Nifty 50 Data Fetched Successfully via Upstox API!\n"
                "🟢 *CE / PE Tracking Active*"
            )
            send_telegram(msg, chat_id=FREE_CHAT_ID)
        else:
            print("Upstox Error fetching data:", data)
    except Exception as e:
        print(f"Upstox Exception occurred: {e}")

# ==========================================
# 1. VIP ADVANCED INTRADAY OPTIONS (CE/PE)
# ==========================================
def generate_advanced_intraday_options_signals():
    print("⚡ Screening Advanced Intraday Options (CE/PE) with 3-Targets...")
    indices = {"^NSEI": "NIFTY 50", "^NSEBANK": "BANK NIFTY"}
    
    for symbol, name in indices.items():
        try:
            df = yf.download(symbol, period="5d", interval="15m", auto_adjust=True, progress=False)
            if df is None or df.empty:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df['Close'].iloc[-1]
            ema9 = df['Close'].ewm(span=9, adjust=False).mean().iloc[-1]
            ema21 = df['Close'].ewm(span=21, adjust=False).mean().iloc[-1]

            step = 50 if "NIFTY 50" in name else 100
            atm_strike = round(close / step) * step

            if ema9 > ema21:
                option_type = "CALL (CE) 📈"
                option_symbol = f"{name} {atm_strike} CE"
                t1, t2, t3 = close * 1.004, close * 1.008, close * 1.015
                sl = close * 0.997
                exit_rule = "Cost-to-Cost trail చేయండి లేదా EMA21 బ్రేక్ అయితే ఎగ్జిట్ అవ్వండి."
            else:
                option_type = "PUT (PE) 📉"
                option_symbol = f"{name} {atm_strike} PE"
                t1, t2, t3 = close * 0.996, close * 0.992, close * 0.985
                sl = close * 1.003
                exit_rule = "డౌన్‌సైడ్ T1 రీచ్ అయినప్పుడు 50% ప్రాఫిట్ బుక్ చేసుకోండి."

            vip_options_msg = (
                f"🚨 *QUANTUM AI VIP ADVANCED OPTION SIGNAL* 🚨\n\n"
                f"📊 *Index:* `{name}`\n"
                f"🎯 *Option Strike:* `{option_symbol}`\n"
                f"⚡ *Signal Type:* *{option_type}*\n"
                f"💵 *Spot Price:* ₹{close:.2f}\n\n"
                f"🎯 *Target 1:* ₹{t1:.2f} (Book 40%)\n"
                f"🎯 *Target 2:* ₹{t2:.2f} (Book 40%)\n"
                f"🎯 *Target 3:* ₹{t3:.2f} (Trail Rest)\n"
                f"🛑 *Stop Loss:* ₹{sl:.2f}\n"
                f"⚠️ *Exit Rule:* _{exit_rule}_\n\n"
                f"💡 _High Risk Management: Use strict SL._"
            )

            free_options_msg = (
                f"📊 *QUANTUM AI OPTIONS MARKET UPDATE*\n\n"
                f"🔹 *Index:* {name}\n"
                f"🔹 *Current Price:* ₹{close:.2f}\n"
                f"🔹 *Trend:* {'BULLISH 🟢' if ema9 > ema21 else 'BEARISH 🔴'}\n\n"
                f"⭐ *Want Live 3-Target Option Strike Signals with SL?*\n"
                f"Join VIP Group: https://mujahidsdghf-bot.github.io/-SMGHFBot/"
            )

            send_telegram(vip_options_msg, chat_id=VIP_CHAT_ID)
            send_telegram(free_options_msg, chat_id=FREE_CHAT_ID)
            time.sleep(1)

        except Exception as e:
            print(f"Error processing options for {name}: {e}")

# ==========================================
# MASTER 200+ STOCKS & CRYPTO LIST
# ==========================================
MASTER_200_LIST = {
    "🔥 [ 1. Nifty 50 & హెవీవెయిట్స్ ]": {
        "^NSEI": "Nifty 50", "^NSEBANK": "Nifty Bank", "RELIANCE.NS": "Reliance", "TCS.NS": "TCS",
        "HDFCBANK.NS": "HDFC Bank", "ICICIBANK.NS": "ICICI Bank", "INFY.NS": "Infosys", "SBIN.NS": "SBI",
        "BHARTIARTL.NS": "Airtel", "ITC.NS": "ITC", "KOTAKBANK.NS": "Kotak Bank", "LT.NS": "L&T",
        "HINDUNILVR.NS": "HUL", "AXISBANK.NS": "Axis Bank", "ASIANPAINT.NS": "Asian Paints", "MARUTI.NS": "Maruti",
        "TITAN.NS": "Titan", "SUNPHARMA.NS": "Sun Pharma", "BAJFINANCE.NS": "Bajaj Finance", "ULTRACEMCO.NS": "UltraTech"
    },
    "⚡ [ 2. ఆటో, మెటల్ & ఎనర్జీ ]": {
        "TATAMOTORS.NS": "Tata Motors", "M&M.NS": "M&M", "BAJAJ-AUTO.NS": "Bajaj Auto", "TVSMOTOR.NS": "TVS Motor",
        "EICHERMOT.NS": "Eicher", "HEROMOTOCO.NS": "Hero MotoCorp", "ASHOKLEY.NS": "Ashok Leyland", "TATASTEEL.NS": "Tata Steel",
        "HINDALCO.NS": "Hindalco", "JSWSTEEL.NS": "JSW Steel", "JINDALSTEL.NS": "Jindal Steel", "SAIL.NS": "SAIL",
        "NMDC.NS": "NMDC", "COALINDIA.NS": "Coal India", "ONGC.NS": "ONGC", "BPCL.NS": "BPCL",
        "HINDPETRO.NS": "HPCL", "IOC.NS": "IOC", "GAIL.NS": "GAIL", "ADANIENT.NS": "Adani Ent"
    },
    "💊 [ 3. ఫార్మా, ఐటీ & కన్స్యూమర్ ]": {
        "ADANIPORTS.NS": "Adani Ports", "DRREDDY.NS": "Dr Reddy", "CIPLA.NS": "Cipla", "DIVISLAB.NS": "Divis Lab",
        "APOLLOHOSP.NS": "Apollo Hosp", "LUPIN.NS": "Lupin", "TORNTPHARM.NS": "Torrent Pharma", "BIOCON.NS": "Biocon",
        "AUROPHARMA.NS": "Aurobindo", "WIPRO.NS": "Wipro", "HCLTECH.NS": "HCL Tech", "TECHM.NS": "Tech Mahindra",
        "LTIM.NS": "LTIMindtree", "PERSISTENT.NS": "Persistent", "COFORGE.NS": "Coforge", "MPHASIS.NS": "Mphasis",
        "NESTLEIND.NS": "Nestle", "BRITANNIA.NS": "Britannia", "TATACONSUM.NS": "Tata Consumer", "DABUR.NS": "Dabur"
    },
    "riven [ 4. బ్యాంకింగ్ & ఫైనాన్స్ ]": {
        "MARICO.NS": "Marico", "GODREJCP.NS": "Godrej CP", "SBILIFE.NS": "SBI Life", "HDFCLIFE.NS": "HDFC Life",
        "INDUSINDBK.NS": "IndusInd Bank", "BANKBARODA.NS": "Bank of Baroda", "PNB.NS": "PNB", "CANBK.NS": "Canara Bank",
        "AUBANK.NS": "AU Bank", "FEDERALBNK.NS": "Federal Bank", "IDFCFIRSTB.NS": "IDFC First", "CHOLAFIN.NS": "Cholamandalam",
        "MUTHOOTFIN.NS": "Muthoot", "SHRIRAMFIN.NS": "Shriram Fin", "DLF.NS": "DLF", "GODREJPROP.NS": "Godrej Prop",
        "OBEROIRLTY.NS": "Oberoi Realty", "SIEMENS.NS": "Siemens", "ABB.NS": "ABB", "BHEL.NS": "BHEL"
    },
    "🚀 [ 5. డిఫెన్స్, పీఎస్‌యూ & రెల్ ]": {
        "AMBUJACEM.NS": "Ambuja", "ACC.NS": "ACC", "SRF.NS": "SRF", "DEEPAKNT.NS": "Deepak Nitrite",
        "NAUKRI.NS": "Naukri", "ZOMATO.NS": "Zomato", "HAL.NS": "HAL", "BEL.NS": "BEL",
        "IRCTC.NS": "IRCTC", "RVNL.NS": "RVNL", "IRFC.NS": "IRFC", "PFC.NS": "PFC",
        "RECLTD.NS": "REC Ltd", "HUDCO.NS": "HUDCO", "IREDA.NS": "IREDA", "CDSL.NS": "CDSL",
        "MCX.NS": "MCX", "IDEA.NS": "Idea", "YESBANK.NS": "Yes Bank", "IDBI.NS": "IDBI Bank"
    },
    "💎 [ 6. పెన్నీ & గ్రోత్ స్టాక్స్ ]": {
        "SOUTHBANK.NS": "South Indian Bank", "SUZLON.NS": "Suzlon", "RPOWER.NS": "Reliance Power", "JPPOWER.NS": "JP Power",
        "PAYTM.NS": "Paytm", "POLICYBABA.NS": "Policybazaar", "NYKAA.NS": "Nykaa", "DELHIVERY.NS": "Delhivery",
        "MAPMYINDIA.NS": "MapmyIndia", "TATAPOWER.NS": "Tata Power", "ADANIGREEN.NS": "Adani Green", "TORNTPOWER.NS": "Torrent Power",
        "NHPC.NS": "NHPC", "SJVN.NS": "SJVN", "VEDL.NS": "Vedanta", "MAZDOCK.NS": "Mazagon Dock",
        "COCHINSHIP.NS": "Cochin Ship", "BDL.NS": "BDL", "BSE.NS": "BSE Ltd", "CAMS.NS": "CAMS"
    },
    "🪙 [ 7. అదనపు స్టాక్స్ & క్రిప్టో ]": {
        "GLENMARK.NS": "Glenmark", "ALKEM.NS": "Alkem", "IPCALAB.NS": "IPCA Labs", "SBICARD.NS": "SBI Cards",
        "ICICIGI.NS": "ICICI Lombard", "ICICIPRULI.NS": "ICICI Pru", "NAVINFLUOR.NS": "Navin Fluorine", "ATUL.NS": "Atul",
        "AARTIIND.NS": "Aarti Ind", "PIIND.NS": "PI Ind", "COROMANDEL.NS": "Coromandel", "UPL.NS": "UPL",
        "TATACHEM.NS": "Tata Chem", "BALKRISIND.NS": "Balkrishna", "MRF.NS": "MRF", "EXIDEIND.NS": "Exide",
        "AMARAJABAT.NS": "Amara Raja", "BRIGADE.NS": "Brigade", "PRESTIGE.NS": "Prestige", "PHOENIXLTD.NS": "Phoenix",
        "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "SOL-USD": "Solana", "XRP-USD": "XRP", "DOGE-USD": "Dogecoin"
    }
}

# ==========================================
# 2. VIP INTRADAY & NORMAL/SWING SCREENER
# ==========================================
def analyze_market_advanced(symbol, name):
    try:
        df = yf.download(symbol, period="20d", interval="1d", auto_adjust=True, progress=False)
        if df is None or df.empty or len(df) < 10:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df['Close']
        ema9 = close.ewm(span=9, adjust=False).mean()
        ema21 = close.ewm(span=21, adjust=False).mean()

        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - close.shift())
        low_close = np.abs(df['Low'] - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        
        last_price = close.iloc[-1]
        atr = atr if not np.isnan(atr) else (last_price * 0.02)

        c_buy = (ema9.iloc[-1] > ema21.iloc[-1]) and (rsi.iloc[-1] > 48)
        sig_intra = "STRONG BUY 🟢" if (c_buy and (last_price > ema9.iloc[-1])) else "HOLD 🟡"

        t1_i = last_price + (1.0 * atr)
        t2_i = last_price + (2.0 * atr)
        t3_i = last_price + (3.5 * atr)
        sl_i = max(0.000001, last_price - (1.2 * atr))

        t1_n = last_price + (2.5 * atr)
        t2_n = last_price + (5.0 * atr)
        t3_n = last_price + (8.0 * atr)
        sl_n = max(0.000001, last_price - (2.5 * atr))

        curr = "$" if "USD" in symbol else "₹"
        p_str = f"{last_price:.2f}" if last_price > 0.01 else f"{last_price:.6f}"
        
        return (
            f"📌 *{name}* (`{symbol}`)\n"
            f"  💵 లైవ్ ధర: {curr}{p_str} | RSI: `{rsi.iloc[-1]:.1f}` | Signal: *{sig_intra}*\n\n"
            f"  ⚡ **1. ఇంట్రాడే (Intraday) Signal:**\n"
            f"    • 🎯 *T1:* {curr}{t1_i:.2f} | *T2:* {curr}{t2_i:.2f} | *T3:* {curr}{t3_i:.2f}\n"
            f"    • 🛑 *SL:* {curr}{sl_i:.2f} | ⚠️ *Exit:* 3:15 PM లోపు లేదా T1 వద్ద కాస్ట్-టూ-కాస్ట్.\n\n"
            f"  📈 **2. నార్మల్ / స్వింగ్ (Normal/Swing) Signal:**\n"
            f"    • 🎯 *T1:* {curr}{t1_n:.2f} | *T2:* {curr}{t2_n:.2f} | *T3:* {curr}{t3_n:.2f}\n"
            f"    • 🛑 *SL:* {curr}{sl_n:.2f} | ⚠️ *Exit:* ట్రెండ్ లేదా ఎస్ఎల్ బ్రేక్ అయితే ఎగ్జిట్.\n"
            f"-----------------------------------"
        )
    except Exception:
        return None

# ==========================================
# MAIN EXECUTION SCRIPT
# ==========================================
if __name__ == "__main__":
    send_telegram(
        "🚀 *QUANTUM AI FREE UPDATE*\n\n"
        "200+ స్టాక్స్ మరియు ఇంట్రాడే ఆప్షన్స్ లైవ్ స్క్రీనింగ్ రన్ అవుతోంది!\n"
        "⭐ అడ్వాన్స్‌డ్ ఇంట్రాడే, నార్మల్/స్వింగ్, మరియు 3-టార్గెట్స్ ఆప్షన్ సిగ్నల్స్ కోసం మన **VIP ఛానెల్** లో చేరండి!\n\n"
        "🔗 *Subscription Link:* https://mujahidsdghf-bot.github.io/-SMGHFBot/",
        chat_id=FREE_CHAT_ID
    )

    send_telegram("🚨 *QUANTUM AI VIP: Multi-Trading Screener Started (Intraday + Normal + Options)...*", chat_id=VIP_CHAT_ID)

    check_option_chain_data()
    generate_advanced_intraday_options_signals()

    for cat_name, items in MASTER_200_LIST.items():
        lines = [f"{cat_name}\n======================="]
        for symbol, name in items.items():
            block = analyze_market_advanced(symbol, name)
            if block:
                lines.append(block)
                if len("\n".join(lines)) > 3500:
                    send_telegram("\n".join(lines), chat_id=VIP_CHAT_ID)
                    lines = [f"{cat_name} (Continuation)\n======================="]

        if len(lines) > 1:
            send_telegram("\n".join(lines), chat_id=VIP_CHAT_ID)
        time.sleep(0.5)

    send_telegram("✅ **అన్ని 200+ స్టాక్స్ మరియు ఆప్షన్స్ స్క్రీనింగ్ విజయవంతంగా పూర్తయింది!**", chat_id=FREE_CHAT_ID)
    send_telegram(
        "✅ *VIP MULTI-MARKET SCREENING COMPLETED!*\n\n"
        "💡 _సూచన: టార్గెట్ 1 వద్ద కనీసం 40% క్వాంటిటీ బుక్ చేసి, స్టాప్ లాస్‌ను కాస్ట్-టూ-కాస్ట్ (Cost-to-Cost) కి మార్చండి._\n\n"
        "🌐 సబ్స్క్రిప్షన్ రెన్యువల్ లేదా సహాయం కోసం: https://mujahidsdghf-bot.github.io/-SMGHFBot/",
        chat_id=VIP_CHAT_ID
    )
    print("Advanced Master Stocks & Options Signals Processed Successfully!")
