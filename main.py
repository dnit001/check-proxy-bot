import os
import telebot
import requests
import time
from flask import Flask, request

# --- CẤU HÌNH ---
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# THÔNG TIN PROXY CỐ ĐỊNH CỦA BẠN
# Tôi đã gán sẵn thông tin bạn cung cấp vào đây
PROXY_HOST = "ipv4-vnpt-01.resvn.net"
PROXY_PORT = "20973"
PROXY_USER = "KG6vsZTt"
PROXY_PASS = "YQlGrmFZYtK7"

@app.route('/')
def index():
    return "Bot is running with fixed Proxy!", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

# --- LỆNH /XOAY TỰ ĐỘNG ---
@bot.message_handler(commands=['xoay'])
def check_proxy_fixed(message):
    try:
        # Thông báo ngay khi nhận lệnh
        bot.reply_to(message, "⏳ Đang tiến hành xoay IP... Vui lòng đợi 10 giây.")
        
        # Đợi 10 giây theo yêu cầu của bạn
        time.sleep(10)

        # Thiết lập kết nối qua Proxy cố định
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

        # Thực hiện truy vấn kiểm tra IP
        # Sử dụng thêm tham số timeout để tránh treo bot nếu proxy lỗi
        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=20)
        data = response.json()

        if data.get('status') == 'success':
            res = (
                f"✅ **XOAY IP THÀNH CÔNG**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📍 Vị trí: {data.get('country')} - {data.get('city')}\n"
                f"🏢 ISP: {data.get('isp')}\n"
                f"🌐 IP Hiện tại: `{data.get('query')}`\n"
                f"━━━━━━━━━━━━━━━"
            )
        else:
            res = "❌ Kết nối được Proxy nhưng API không trả về dữ liệu vị trí."
            
        bot.reply_to(message, res, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ **LỖI KẾT NỐI**\nProxy có thể chưa kịp sống lại sau khi xoay hoặc sai thông tin xác thực.\n`Chi tiết: {str(e)}`")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
