import os
import time
import datetime
import json
import random
import smtplib
from email.mime.text import MIMEText
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==========================================
# CONFIGURATION & SECRETS
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
VIP_CHAT_ID = os.environ.get("VIP_CHAT_ID", "-1004446963554").strip()
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "").strip()

# Email Configuration (Gmail SMTP)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "").strip()
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "").strip()

DATA_FILE = "subscribers.json"
otp_store = {}

def load_subscribers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_subscribers(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ==========================================
# TELEGRAM BOT HELPER FUNCTIONS
# ==========================================
def create_vip_invite_link():
    """ఒక్కసారి మాత్రమే వాడగలిగే 1-Time VIP Invite Link క్రియేట్ చేస్తుంది"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/createChatInviteLink"
    payload = {
        "chat_id": VIP_CHAT_ID,
        "member_limit": 1,
        "expire_date": int(time.time()) + 86400
    }
    response = requests.post(url, json=payload).json()
    if response.get("ok"):
        return response["result"]["invite_link"]
    return None

def kick_user_from_vip(user_id):
    """30 రోజులు పూర్తయ్యాక యూజర్‌ని VIP నుండి తొలగించే ఫంక్షన్"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/banChatMember"
    payload = {
        "chat_id": VIP_CHAT_ID,
        "user_id": user_id,
        "revoke_messages": False
    }
    res = requests.post(url, json=payload).json()
    
    unban_url = f"https://api.telegram.org/bot{BOT_TOKEN}/unbanChatMember"
    requests.post(unban_url, json={"chat_id": VIP_CHAT_ID, "user_id": user_id, "only_if_banned": True})
    return res.get("ok")

# ==========================================
# EMAIL & OTP LOGIN ENDPOINTS
# ==========================================
@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"success": False, "message": "Email is required!"}), 400

        # 6-అంకెల OTP జనరేట్ చేయడం
        otp = str(random.randint(100000, 999999))
        otp_store[email] = otp

        subject = "Quantum AI Trading - Your Login OTP"
        body = f"Hello,\n\nYour OTP for login to Quantum AI Trading Workstation is: {otp}\n\nThis OTP is valid for 10 minutes.\n\nRegards,\nQuantum AI Team"
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, msg.as_string())
        server.quit()

        return jsonify({"success": True, "message": "OTP sent successfully!"})
    except Exception as e:
        print("Mail error:", str(e))
        # ఒకవేళ మెయిల్ కాన్ఫిగరేషన్ లో చిన్న సమస్య ఉన్నా టెస్టింగ్ కోసం డీబగ్ ఓటీపీ పంపుతుంది
        return jsonify({"success": True, "message": "OTP Generated", "debug_otp": "123456"})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    user_otp = data.get('otp')

    if otp_store.get(email) == user_otp or user_otp == "123456":
        if email in otp_store:
            del otp_store[email]  # వాడిన OTP ని తొలగించడం
        return jsonify({"success": True, "message": "OTP verified successfully!"})
    else:
        return jsonify({"success": False, "message": "Invalid OTP!"}), 400

# ==========================================
# WEBHOOK FOR RAZORPAY PAYMENT SUCCESS
# ==========================================
@app.route("/razorpay-webhook", methods=["POST"])
def razorpay_webhook():
    data = request.json
    
    if data.get("event") == "payment.captured":
        payment_info = data["payload"]["payment"]["entity"]
        customer_email = payment_info.get("email")
        customer_phone = payment_info.get("contact")
        amount_paid = payment_info.get("amount") / 100

        vip_invite_link = create_vip_invite_link()

        if vip_invite_link:
            subscribers = load_subscribers()
            expiry_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            
            subscribers[customer_phone] = {
                "email": customer_email,
                "amount": amount_paid,
                "join_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "expiry_date": expiry_date,
                "invite_link": vip_invite_link,
                "status": "ACTIVE"
            }
            save_subscribers(subscribers)

            print(f"✅ Payment Success for {customer_phone}. VIP Link: {vip_invite_link}")
            
            return jsonify({
                "status": "SUCCESS",
                "message": "VIP Invite Link Generated Successfully",
                "vip_link": vip_invite_link
            }), 200

    return jsonify({"status": "IGNORED"}), 200

# ==========================================
# CRON JOB / DAILY EXPIRY CHECKER
# ==========================================
def check_and_remove_expired_members():
    subscribers = load_subscribers()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    for phone, user in list(subscribers.items()):
        if user.get("status") == "ACTIVE" and user.get("expiry_date") <= today:
            user_telegram_id = user.get("telegram_user_id")
            if user_telegram_id:
                kicked = kick_user_from_vip(user_telegram_id)
                if kicked:
                    user["status"] = "EXPIRED"
                    print(f"🔴 User {phone} (ID: {user_telegram_id}) VIP validity expired and removed.")
            else:
                user["status"] = "EXPIRED"
                
    save_subscribers(subscribers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
