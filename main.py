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

# THÔNG TIN PROXY VNPT
P_HOST = "ipv4-vnpt-01.resvn.net"
P_PORT = "20973"
P_USER = "KG6vsZTt"
P_PASS = "YQlGrmFZYtK7"

# URL API XOAY CỦA NHÀ MẠNG
ROTATE_API_URL = "https://client.cloudmini.net/api/v2/change_ip?api_key=f1155859bb08c3262ebeff072fbfd196ad3b81eb&id=413714"

@app.route('/')
def health_check():
    return "Bot is running with Auto-Rotate API!", 200

@bot.message_handler(commands=['xoay'])
def handle_xoay(message):
    try:
        # BƯỚC 1: GỬI LỆNH XOAY ĐẾN NHÀ MẠNG
        bot.reply_to(message, "🔄 Đang gửi yêu cầu xoay IP tới nhà mạng VN Cloud Mini...")
        rotate_res = requests.get(ROTATE_API_URL, timeout=15)
        
        # BƯỚC 2: ĐỢI 15 GIÂY
        bot.send_message(message.chat.id, "⏳ Đang đợi 30 giây để hệ thống đổi IP mới...")
        time.sleep(30)

        # BƯỚC 3: KIỂM TRA VỊ TRÍ QUA PROXY
        bot.send_message(message.chat.id, "🔍 Đang kiểm tra vị trí IP mới...")
        
        proxy_url = f"http://{P_USER}:{P_PASS}@{P_HOST}:{P_PORT}"
        proxies = {"http": proxy_url, "https": proxy_url}
        
        # Gọi API lấy vị trí (Sử dụng ip-api.com)
        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=20)
        data = response.json()
        
        if data.get('status') == 'success':
            msg = (f"✅ **XOAY & CHECK THÀNH CÔNG**\n"
                   f"━━━━━━━━━━━━━━━\n"
                   f"🏙 **Thành phố:** {data.get('city')}\n"
                   f"🗺 **Tỉnh/Vùng:** {data.get('regionName')}\n"
                   f"🏢 **Nhà mạng:** {data.get('isp')}\n"
                   f"🌐 **IP Mới:** `{data.get('query')}`\n"
                   f"━━━━━━━━━━━━━━━")
        else:
            msg = "❌ Đã xoay nhưng không lấy được dữ liệu IP (Proxy có thể đang khởi động lại)."
        
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ **LỖI HỆ THỐNG**\n`{str(e)}`")

def run_polling():
    bot.remove_webhook()
    time.sleep(1)
    print("Bot is starting polling...")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    # Chạy Bot trong luồng riêng
    threading.Thread(target=run_polling, daemon=True).start()
    
    # Chạy Flask Server cho Koyeb
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
