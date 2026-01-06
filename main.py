import os
import telebot
import requests
import time
import threading
from flask import Flask
from bs4 import BeautifulSoup
from lxml import etree

# --- CẤU HÌNH ---
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# THÔNG TIN PROXY VNPT
P_HOST, P_PORT, P_USER, P_PASS = "ipv4-vnpt-01.resvn.net", "20973", "KG6vsZTt", "YQlGrmFZYtK7"
proxy_url = f"http://{P_USER}:{P_PASS}@{P_HOST}:{P_PORT}"
proxies = {"http": proxy_url, "https": proxy_url}

@app.route('/')
def health_check():
    return "Bot is running with Etsy check support!", 200

# --- HÀM CHECK ETSY ---
@bot.message_handler(commands=['checketsy'])
def handle_check_etsy(message):
    try:
        url = "https://www.etsy.com/shop/boongke/?etsrc=sdt"
        bot.reply_to(message, "🔍 Đang truy cập Etsy qua Proxy VNPT để lấy dữ liệu...")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

        # Gửi request qua Proxy
        response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
        
        if response.status_code != 200:
            bot.reply_to(message, f"❌ Không thể truy cập Etsy. Lỗi HTTP: {response.status_code}")
            return

        # Parse HTML
        soup = BeautifulSoup(response.content, "html.parser")
        dom = etree.HTML(str(soup))

        # 1. Lấy Shop Name bằng Class
        shop_name_tag = soup.find("h1", class_="shop-name wt-text-title-larger wt-text-truncate")
        shop_name = shop_name_tag.text.strip() if shop_name_tag else "Không tìm thấy"

        # 2. Lấy dữ liệu theo các XPath bạn cung cấp
        def get_by_xpath(xpath_str):
            result = dom.xpath(xpath_str)
            return result[0].text.strip() if result and hasattr(result[0], 'text') else "N/A"

        # Các XPath của bạn
        data_1 = get_by_xpath('//*[@id="shop-home-header"]/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div[3]/div/div[1]')
        data_2 = get_by_xpath('//*[@id="shop-home-header"]/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div[5]')
        data_3 = get_by_xpath('//*[@id="shop-home-header"]/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div[1]/div/div')

        # Gửi kết quả
        res_msg = (
            f"🏪 **THÔNG TIN SHOP ETSY**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🏷 **Shop Name:** {shop_name}\n"
            f"📊 **Số liệu 1:** {data_1}\n"
            f"📊 **Số liệu 2:** {data_2}\n"
            f"📊 **Số liệu 3:** {data_3}\n"
            f"━━━━━━━━━━━━━━━"
        )
        bot.reply_to(message, res_msg, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi lấy dữ liệu Etsy: {str(e)}")

# --- GIỮ NGUYÊN LỆNH /XOAY CŨ ---
@bot.message_handler(commands=['xoay'])
def handle_xoay(message):
    try:
        bot.reply_to(message, "🔌 Đang gửi lệnh xoay IP...")
        requests.get("https://client.cloudmini.net/api/v2/change_ip?api_key=f1155859bb08c3262ebeff072fbfd196ad3b81eb&id=413714", timeout=15)
        bot.send_message(message.chat.id, "⏳ Đợi 20 giây...")
        time.sleep(20)
        
        response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=20)
        data = response.json()
        if data.get('status') == 'success':
            msg = f"✅ **XOAY THÀNH CÔNG**\n🏙 Thành phố: {data.get('city')}\n🌐 IP: `{data.get('query')}`"
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
