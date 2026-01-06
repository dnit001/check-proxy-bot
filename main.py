import os
import telebot
import requests
import time
import threading
from flask import Flask
from bs4 import BeautifulSoup
from lxml import etree

# --- CẤU HÌNH BOT ---
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- CẤU HÌNH SOCKS5 MỚI ---
SOCKS5_URL = "socks5://proxy:dhTyavT@easyport.mobilehop.com:28421"
proxies = {
    "http": SOCKS5_URL,
    "https": SOCKS5_URL
}

# URL API XOAY NHÀ MẠNG (Giữ nguyên để bạn vẫn dùng được lệnh /xoay)
ROTATE_API_URL = "https://client.cloudmini.net/api/v2/change_ip?api_key=f1155859bb08c3262ebeff072fbfd196ad3b81eb&id=413714"

@app.route('/')
def health_check():
    return "Bot is running with SOCKS5 Proxy!", 200

# --- LỆNH CHECK ETSY ---
@bot.message_handler(commands=['checketsy'])
def handle_check_etsy(message):
    try:
        url = "https://www.etsy.com/shop/boongke/?etsrc=sdt"
        bot.reply_to(message, "🔍 Đang truy cập Etsy qua SOCKS5...")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }

        # Gửi request qua SOCKS5
        response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
        
        if response.status_code != 200:
            bot.reply_to(message, f"❌ Lỗi HTTP: {response.status_code} (Etsy có thể vẫn đang chặn IP này)")
            return

        soup = BeautifulSoup(response.content, "html.parser")
        dom = etree.HTML(str(soup))

        shop_name_tag = soup.find("h1", class_="shop-name wt-text-title-larger wt-text-truncate")
        shop_name = shop_name_tag.text.strip() if shop_name_tag else "N/A"

        def get_by_xpath(xpath_str):
            result = dom.xpath(xpath_str)
            if result:
                return result[0].text.strip() if hasattr(result[0], 'text') and result[0].text else str(result[0]).strip()
            return "N/A"

        data_1 = get_by_xpath('//*[@id="shop-home-header"]/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div[3]/div/div[1]')
        data_2 = get_by_xpath('//*[@id="shop-home-header"]/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div[5]')
        data_3 = get_by_xpath('//*[@id="shop-home-header"]/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div[1]/div/div')

        res_msg = (
            f"🏪 **ETSY SHOP INFO (via SOCKS5)**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🏷 **Shop Name:** {shop_name}\n"
            f"📊 **Data 1:** {data_1}\n"
            f"📊 **Data 2:** {data_2}\n"
            f"📊 **Data 3:** {data_3}\n"
            f"━━━━━━━━━━━━━━━"
        )
        bot.reply_to(message, res_msg, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

# --- LỆNH XOAY IP (Vẫn giữ nguyên cho bạn) ---
@bot.message_handler(commands=['xoay'])
def handle_xoay(message):
    try:
        bot.reply_to(message, "🔌 Đang gửi lệnh xoay IP tới nhà mạng...")
        requests.get(ROTATE_API_URL, timeout=15)
        bot.send_message(message.chat.id, "⏳ Đợi 20 giây để IP mới cập nhật vào SOCKS5...")
        time.sleep(20)
        
        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=20)
        data = response.json()
        if data.get('status') == 'success':
            msg = f"✅ **XOAY THÀNH CÔNG**\n🏙 Thành phố: {data.get('city')}\n🌐 IP Mới: `{data.get('query')}`"
            bot.send_message(message.chat.id, msg, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

def run_polling():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_polling, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
