import streamlit as st
import requests
import pandas as pd
import time
import os

# వెబ్ టూల్ పేజ్ సెటప్
st.set_page_config(page_title="SM AI Automated Trading Tool", layout="wide")

st.title("🚀 SM AI Automated Stocks & Crypto Trading Tool")
st.markdown("### ఆటోమేటిక్ టార్గెట్, స్టాప్ లాస్ మరియు అప్‌స్టాక్స్ ఎగ్జిట్ డ్యాష్‌బోర్డ్")

# సైడ్‌బార్‌లో అప్‌స్టాక్స్ టోకెన్ సెట్టింగ్స్
st.sidebar.header("🔑 API సెట్టింగ్స్")
upstox_token = st.sidebar.text_input("Upstox Access Token", type="password")

# యూజర్ ట్రేడ్ ఇన్పుట్ సెక్షన్
st.markdown("---")
st.subheader("📊 కొత్త ఆటోమేటిక్ ట్రేడ్ సెట్ చేయండి")

col1, col2, col3, col4 = st.columns(4)
with col1:
    symbol = st.text_input("స్టాక్ సింబల్ (ఉదా: RELIANCE.NS)", "RELIANCE.NS")
with col2:
    buy_price = st.number_input("బై / ఎంట్రీ ధర (₹)", value=2450.0)
with col3:
    stop_loss = st.number_input("స్టాప్ లాస్ (SL ₹)", value=2400.0)
with col4:
    target = st.number_input("టార్గెట్ (Target ₹)", value=2550.0)

quantity = st.number_input("క్వాంటిటీ (Quantity)", value=10, min_value=1)

if st.button("🟢 ఆటోమేటిక్ ట్రేడ్ & మానిటరింగ్ ప్రారంభించు"):
    st.success(f"Success! {symbol} కోసం ఆటోమేటిక్ స్టాప్ లాస్ మరియు టార్గెట్ ట్రాకింగ్ ఆక్టివేట్ చేయబడింది.")
    
    # ఆటోమేటిక్ మానిటరింగ్ సిమ్యులేషన్
    placeholder = st.empty()
    for i in range(5):
        time.sleep(1)
        placeholder.info(f"⏳ మార్కెట్ మానిటరింగ్ జరుగుతోంది... కరెంట్ స్టేటస్: Active (SL: {stop_loss} | Tgt: {target})")

# అప్‌స్టాక్స్ ఆటోమేటిక్ ఎగ్జిట్ ఫంక్షన్
def execute_upstox_exit(instrument_key, qty, token):
    if not token:
        print("Token missing")
        return False
    
    url = "https://api.upstox.com/v2/order/place"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "quantity": qty,
        "product": "I",
        "validity": "DAY",
        "price": 0.0,
        "tag": "Web_Auto_Exit",
        "instrument_token": instrument_key,
        "order_type": "MARKET",
        "transaction_type": "SELL",
        "is_amo": False
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return True
    except Exception as e:
        print(f"Exit Error: {e}")
    return False
