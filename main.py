import telebot
import requests
import threading
from flask import Flask
import os

# --- CẤU HÌNH BOT ---
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)

# --- WEB SERVER ĐỂ VƯỢT QUA HEALTH CHECK ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    # Koyeb/Render cung cấp cổng qua biến môi trường PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- LOGIC CHECK PROXY ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ Bot đã sẵn sàng! Gửi: `/vitri host:port:user:pass`", parse_mode='Markdown')

@bot.message_handler(commands=['vitri'])
def check_proxy(message):
    try:
        input_text = message.text.replace("/vitri", "").strip()
        if not input_text:
            bot.reply_to(message, "⚠️ Nhập theo mẫu: `/vitri host:port:user:pass`")
            return

        parts = input_text.split(':')
        if len(parts) != 4:
            bot.reply_to(message, "❌ Định dạng sai!")
            return

        host, port, user, password = parts
        proxy_url = f"http://{user}:{password}@{host}:{port}"
        proxies = {"http": proxy_url, "https": proxy_url}

        bot.send_chat_action(message.chat.id, 'typing')
        
        # Gọi API kiểm tra
        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=15)
        data = response.json()

        if data.get('status') == 'success':
            res = (f"✅ **LIVE**\n📍 Quốc gia: {data.get('country')}\n"
                   f"🏢 ISP: {data.get('isp')}\n🌐 IP: `{data.get('query')}`")
        else:
            res = "❌ Proxy kết nối được nhưng không lấy được vị trí."
        
        bot.reply_to(message, res, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi kết nối: {str(e)}")

# --- CHẠY SONG SONG BOT VÀ WEB SERVER ---
if __name__ == "__main__":
    # Chạy Web Server ở một luồng riêng
    threading.Thread(target=run_web).start()
    print("Bot đang chạy...")
    # Chạy Telegram Bot
    bot.infinity_polling()
