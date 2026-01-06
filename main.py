import os
import telebot
import cloudscraper
import time
import threading
from flask import Flask
from bs4 import BeautifulSoup
from lxml import etree

# --- CẤU HÌNH BOT ---
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- CẤU HÌNH SOCKS5 MOBILEHOP ---
SOCKS5_URL = "socks5://proxy:dhTyavT@easyport.mobilehop.com:28421"
proxies = {
    "http": SOCKS5_URL,
    "https": SOCKS5_URL
}

@app.route('/')
def health_check():
    return "Bot is running with Cloudscraper!", 200

@bot.message_handler(commands=['checketsy'])
def handle_check_etsy(message):
    try:
        url = "https://www.etsy.com/shop/boongke/?etsrc=sdt"
        bot.reply_to(message, "🛡️ Đang sử dụng Cloudscraper để vượt tường lửa Etsy...")

        # Khởi tạo scraper giả lập trình duyệt Desktop (Chrome)
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

        # Gửi request qua SOCKS5 bằng cloudscraper
        response = scraper.get(url, proxies=proxies, timeout=30)
        
        if response.status_code == 403:
            bot.reply_to(message, "⚠️ Vẫn bị lỗi 403. Etsy đã chặn dải IP của Mobilehop hoặc nhận diện Fingerprint SSL.")
            return
        elif response.status_code != 200:
            bot.reply_to(message, f"❌ Lỗi HTTP: {response.status_code}")
            return

        # Parse dữ liệu
        soup = BeautifulSoup(response.content, "html.parser")
        dom = etree.HTML(str(soup))

        shop_name_tag = soup.find("h1", class_="shop-name wt-text-title-larger wt-text-truncate")
        shop_name = shop_name_tag.text.strip() if shop_name_tag else "N/A"

        def get_by_xpath(xpath_str):
            result = dom.xpath(xpath_str)
            if result:
                return result[0].text.strip() if hasattr(result[0], 'text') and result[0].text else str(result[0]).strip()
            return "N/A"

        # Lấy các thông số bạn yêu cầu
        data_1 = get_by_xpath('//*[@id="shop-home-header"]/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div[3]/div/div[1]')
        data_2 = get_by_xpath('//*[@id="shop-home-header"]/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div[5]')
        data_3 = get_by_xpath('//*[@id="shop-home-header"]/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div[1]/div/div')

        res_msg = (
            f"🏪 **ETSY SHOP INFO**\n"
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

# --- GIỮ NGUYÊN LỆNH /XOAY VÀ START POLLING ---
@bot.message_handler(commands=['xoay'])
def handle_xoay(message):
    try:
        bot.reply_to(message, "🔌 Đang gửi lệnh xoay IP...")
        import requests
        requests.get("https://client.cloudmini.net/api/v2/change_ip?api_key=f1155859bb08c3262ebeff072fbfd196ad3b81eb&id=413714", timeout=15)
        bot.send_message(message.chat.id, "⏳ Đợi 20s để IP cập nhật...")
        time.sleep(20)
        res = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=20)
        data = res.json()
        bot.send_message(message.chat.id, f"✅ IP Mới: `{data.get('query')}`")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

def run_polling():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
