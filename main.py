import os
import telebot
import requests
import time
import threading
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

# --- WEB SERVER CHO KOYEB HEALTH CHECK ---
@app.route('/')
def index():
    return "Bot is alive and polling!", 200

# --- LOGIC XỬ LÝ LỆNH /XOAY ---
@bot.message_handler(commands=['xoay'])
def check_proxy_fixed(message):
    try:
        bot.reply_to(message, "⏳ Đã nhận lệnh. Đang xoay IP VNPT, vui lòng đợi 10 giây...")
        
        # Tạm dừng 10 giây theo yêu cầu
        time.sleep(10)

        # Cấu hình Proxy
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        proxies = {"http": proxy_url, "https": proxy_url}

        # Gọi API lấy vị trí (Thêm timeout 20s để tránh treo)
        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=20)
        data = response.json()

        if data.get('status') == 'success':
            res = (
                f"✅ **XOAY IP THÀNH CÔNG**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📍 **Quốc gia:** {data.get('country')}\n"
                f"🏙 **Thành phố:** {data.get('city')}\n"
                f"🗺 **Tỉnh/Vùng:** {data.get('regionName')}\n"
                f"🏢 **Nhà mạng:** {data.get('isp')}\n"
                f"🌐 **IP Mới:** `{data.get('query')}`\n"
                f"━━━━━━━━━━━━━━━"
            )
        else:
            res = "❌ Proxy kết nối được nhưng không lấy được vị trí IP."
            
        bot.reply_to(message, res, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ **LỖI KẾT NỐI**\nCó thể Proxy chưa sẵn sàng hoặc bị Die.\n`Lỗi: {str(e)}`")

# --- HÀM CHẠY BOT ---
def start_bot():
    # Xóa bỏ hoàn toàn Webhook cũ để chuyển sang Polling
    bot.remove_webhook()
    print("Webhook removed. Starting Polling...")
    bot.infinity_polling()

if __name__ == "__main__":
    # 1. Chạy Bot ở luồng phụ (Background Thread)
    threading.Thread(target=start_bot, daemon=True).start()
    
    # 2. Chạy Flask ở luồng chính để Koyeb không báo lỗi Unhealthy
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
