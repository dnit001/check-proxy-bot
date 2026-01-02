import os
import telebot
import requests
from flask import Flask, request

# Cấu hình Token
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Route để Koyeb kiểm tra trạng thái (Health Check)
@app.route('/')
def index():
    return "Bot is running!", 200

# Route để nhận tin nhắn từ Telegram (Webhook)
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

# Logic xử lý lệnh /vitri
@bot.message_handler(commands=['vitri'])
def check_proxy(message):
    try:
        input_text = message.text.replace("/vitri", "").strip()
        parts = input_text.split(':')
        if len(parts) != 4:
            bot.reply_to(message, "❌ Định dạng: `host:port:user:pass`")
            return

        host, port, user, password = parts
        proxy_url = f"http://{user}:{password}@{host}:{port}"
        proxies = {"http": proxy_url, "https": proxy_url}

        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=10)
        data = response.json()

        if data.get('status') == 'success':
            res = (f"✅ **LIVE (Koyeb)**\n📍 Quốc gia: {data['country']}\n"
                   f"🏢 ISP: {data['isp']}\n🌐 IP: `{data['query']}`")
        else:
            res = "❌ Không lấy được vị trí."
        bot.reply_to(message, res, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi kết nối: Proxy Die hoặc sai thông tin.")

if __name__ == "__main__":
    # Koyeb sẽ cung cấp PORT qua biến môi trường
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
