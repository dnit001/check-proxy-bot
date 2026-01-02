import telebot
import requests
from requests.auth import HTTPProxyAuth

# Token của bạn
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🤖 **Bot Check Proxy VNPT (Socks5/HTTPS) sẵn sàng!**\n\n"
        "Hãy gửi lệnh theo mẫu:\n"
        "`/vitri host:port:user:pass`"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['vitri'])
def check_proxy(message):
    try:
        # Lấy nội dung sau lệnh /vitri
        input_text = message.text.replace("/vitri", "").strip()
        
        if not input_text:
            bot.reply_to(message, "⚠️ Vui lòng nhập: `/vitri host:port:user:pass`", parse_mode='Markdown')
            return

        # Tách chuỗi host:port:user:pass
        parts = input_text.split(':')
        if len(parts) != 4:
            bot.reply_to(message, "❌ Định dạng sai! Cần đủ 4 phần `host:port:user:pass` tách nhau bằng dấu `:`")
            return

        host, port, user, password = parts
        
        # Thử nghiệm với cả HTTP và SOCKS5 (Định dạng của bạn thường hỗ trợ cả hai)
        # Chúng ta ưu tiên định dạng HTTP/HTTPS cho proxy của bạn
        proxy_url = f"http://{user}:{password}@{host}:{port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

        bot.send_chat_action(message.chat.id, 'typing')
        msg_wait = bot.reply_to(message, "⏳ Đang kết nối thực tế qua Proxy VNPT...")

        # Gọi API qua Proxy để lấy thông tin IP xuất thực sự
        # Sử dụng API ip-api.com (Chạy trên Python sẽ không bị lỗi 429 như GAS)
        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=15)
        data = response.json()

        if data.get('status') == 'success':
            res_msg = (
                f"✅ **PROXY LIVE**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📍 Quốc gia: {data.get('country')} ({data.get('countryCode')})\n"
                f"🏙 Thành phố: {data.get('city')}\n"
                f"🏢 Nhà mạng: {data.get('isp')}\n"
                f"🌐 IP Xuất: `{data.get('query')}`\n"
                f"━━━━━━━━━━━━━━━"
            )
        else:
            res_msg = "❌ Proxy kết nối được nhưng không lấy được dữ liệu vị trí."

        bot.edit_message_text(res_msg, message.chat.id, msg_wait.message_id, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ **KẾT NỐI THẤT BẠI**\n\nProxy có thể đã DIE hoặc sai thông tin đăng nhập.\n`Lỗi: {str(e)}`")

if __name__ == "__main__":
    print("Bot Python đang chạy...")
    bot.infinity_polling()
