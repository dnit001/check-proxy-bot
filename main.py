import os
import telebot
import requests
import time
from flask import Flask

# --- CẤU HÌNH BOT ---
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# THÔNG TIN PROXY CỐ ĐỊNH
PROXY_HOST = "ipv4-vnpt-01.resvn.net"
PROXY_PORT = "20973"
PROXY_USER = "KG6vsZTt"
PROXY_PASS = "YQlGrmFZYtK7"

@app.route('/')
def index():
    return "Bot status: Healthy", 200

@bot.message_handler(commands=['xoay'])
def check_proxy_fixed(message):
    try:
        bot.reply_to(message, "⏳ Đang xoay IP... Vui lòng đợi 10 giây.")
        time.sleep(10)

        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        proxies = {"http": proxy_url, "https": proxy_url}

        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=20)
        data = response.json()

        if data.get('status') == 'success':
            res = (
                f"✅ **XOAY IP THÀNH CÔNG**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📍 Quốc gia: {data.get('country')}\n"
                f"🏙 Thành phố: {data.get('city')}\n"
                f"🏢 ISP: {data.get('isp')}\n"
                f"🌐 IP: `{data.get('query')}`"
            )
        else:
            res = "❌ Proxy kết nối được nhưng không lấy được dữ liệu vị trí."
        bot.reply_to(message, res, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

# Chạy bot bằng Polling (Cách này đơn giản và ít lỗi hơn Webhook trên Koyeb)
def run_bot():
    print("Starting Bot Polling...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Khởi chạy một thread riêng cho bot để không làm treo Flask
    import threading
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Flask chạy để Koyeb Health Check xanh
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
