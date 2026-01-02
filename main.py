import os
import telebot
import requests
import time
import threading
from flask import Flask

# --- CẤU HÌNH ---
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# PROXY VNPT CỐ ĐỊNH
P_HOST = "ipv4-vnpt-01.resvn.net"
P_PORT = "20973"
P_USER = "KG6vsZTt"
P_PASS = "YQlGrmFZYtK7"

@app.route('/')
def health_check():
    return "Bot VNPT is Active!", 200

@bot.message_handler(commands=['xoay'])
def handle_xoay(message):
    try:
        bot.reply_to(message, "⏳ Đã nhận lệnh. Đang xoay IP và lấy thông tin thành phố (10s)...")
        time.sleep(10)
        
        proxy_url = f"http://{P_USER}:{P_PASS}@{P_HOST}:{P_PORT}"
        proxies = {"http": proxy_url, "https": proxy_url}
        
        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=20)
        data = response.json()
        
        if data.get('status') == 'success':
            msg = (f"✅ **XOAY THÀNH CÔNG**\n"
                   f"━━━━━━━━━━━━━━━\n"
                   f"🏙 **Thành phố:** {data.get('city')}\n"
                   f"🗺 **Tỉnh/Vùng:** {data.get('regionName')}\n"
                   f"🏢 **Nhà mạng:** {data.get('isp')}\n"
                   f"🌐 **IP Hiện tại:** `{data.get('query')}`\n"
                   f"━━━━━━━━━━━━━━━")
        else:
            msg = "❌ Proxy LIVE nhưng không lấy được dữ liệu vị trí."
        bot.reply_to(message, msg, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

def run_polling():
    # Xóa sạch Webhook cũ để chạy Polling
    bot.remove_webhook()
    print("Bot is polling...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Chạy Bot trong luồng riêng
    threading.Thread(target=run_polling, daemon=True).start()
    
    # Chạy Flask Server cho Koyeb
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
