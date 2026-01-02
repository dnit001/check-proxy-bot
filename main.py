import os
import telebot
import requests
import time
from flask import Flask, request

# --- CẤU HÌNH ---
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
    return "Bot is running with City Location support!", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

# --- LỆNH /XOAY TỰ ĐỘNG LẤY THÀNH PHỐ ---
@bot.message_handler(commands=['xoay'])
def check_proxy_fixed(message):
    try:
        bot.reply_to(message, "⏳ Đang xoay IP... Vui lòng đợi 10 giây để lấy vị trí mới.")
        
        # Đợi 10 giây
        time.sleep(10)

        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        proxies = {"http": proxy_url, "https": proxy_url}

        # Gọi API lấy dữ liệu chi tiết
        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=20)
        data = response.json()

        if data.get('status') == 'success':
            # Trích xuất dữ liệu chi tiết hơn
            country = data.get('country', 'N/A')
            city = data.get('city', 'N/A')
            region_name = data.get('regionName', 'N/A') # Tên tỉnh/thành (ví dụ: Ho Chi Minh City)
            isp = data.get('isp', 'N/A')
            ip_query = data.get('query', 'N/A')

            res = (
                f"✅ **XOAY IP THÀNH CÔNG**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📍 **Quốc gia:** {country}\n"
                f"🏙 **Thành phố:** {city}\n"
                f"🗺 **Tỉnh/Vùng:** {region_name}\n"
                f"🏢 **Nhà mạng:** {isp}\n"
                f"🌐 **IP Hiện tại:** `{ip_query}`\n"
                f"━━━━━━━━━━━━━━━"
            )
        else:
            res = "❌ Proxy kết nối được nhưng API không trả về dữ liệu vị trí."
            
        bot.reply_to(message, res, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ **LỖI KẾT NỐI**\nProxy chưa sẵn sàng hoặc gặp sự cố.\n`Lỗi: {str(e)}`")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
