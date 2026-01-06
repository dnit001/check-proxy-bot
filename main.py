import os
import telebot
import time
import threading
from flask import Flask
from bs4 import BeautifulSoup
from lxml import etree
from curl_cffi import requests as curlr # Giả lập Chrome vượt 403

# --- CẤU HÌNH BOT ---
TOKEN = "8322740481:AAFR4Or9Ly__cdDtMtWXH3NO64_ZLNfYYmg"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- CẤU HÌNH PROXY 1: MOBILEHOP (Dùng để check Etsy) ---
MOBILEHOP_SOCKS5 = "socks5://proxy:dhTyavT@easyport.mobilehop.com:28421"
proxies_etsy = {
    "http": MOBILEHOP_SOCKS5,
    "https": MOBILEHOP_SOCKS5
}

# --- CẤU HÌNH PROXY 2: VNPT (Dùng để xoay và check IP VNPT) ---
VNPT_SOCKS5 = "socks5://KG6vsZTt:YQlGrmFZYtK7@ipv4-vnpt-01.resvn.net:22941"
proxies_vnpt = {
    "http": VNPT_SOCKS5,
    "https": VNPT_SOCKS5
}

# API XOAY IP NHÀ MẠNG
ROTATE_API_URL = "https://client.cloudmini.net/api/v2/change_ip?api_key=f1155859bb08c3262ebeff072fbfd196ad3b81eb&id=413714"

@app.route('/')
def health_check():
    return "Bot is active with dual Proxy setup!", 200

# --- LỆNH XOAY (Sử dụng Proxy VNPT) ---
@bot.message_handler(commands=['xoay'])
def handle_xoay(message):
    try:
        bot.reply_to(message, "🔌 Đang gửi lệnh xoay IP cho hệ thống VNPT...")
        
        # Gửi lệnh xoay (không qua proxy)
        import requests as req_basic
        req_basic.get(ROTATE_API_URL, timeout=15)
        
        bot.send_message(message.chat.id, "⏳ Đợi 20 giây để hệ thống VNPT gán IP mới...")
        time.sleep(20)
        
        # Kiểm tra IP mới qua Proxy VNPT
        response = req_basic.get("http://ip-api.com/json/", proxies=proxies_vnpt, timeout=20)
        data = response.json()
        
        msg = (f"✅ **XOAY VNPT THÀNH CÔNG**\n"
               f"🌐 IP Mới: `{data.get('query')}`\n"
               f"🏙 Vị trí: {data.get('city')}, {data.get('country')}")
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi xoay VNPT: {str(e)}")

# --- LỆNH CHECK ETSY (Sử dụng Proxy Mobilehop) ---
@bot.message_handler(commands=['checketsy'])
def handle_check_etsy(message):
    try:
        url = "https://www.etsy.com/shop/boongke/?etsrc=sdt"
        bot.reply_to(message, "🛡️ Đang truy cập Etsy qua Mobilehop SOCKS5 (Chrome Impersonate)...")

        # Dùng curl_cffi giả lập Chrome qua Proxy Mobilehop
        response = curlr.get(
            url, 
            proxies=proxies_etsy, 
            impersonate="chrome120", 
            timeout=30
        )
        
        if response.status_code == 403:
            bot.reply_to(message, "❌ Etsy vẫn chặn (403). Mobilehop IP này có thể đã bị blacklist.")
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
            f"🏪 **ETSY INFO (Mobilehop)**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🏷 **Shop Name:** {shop_name}\n"
            f"📊 Data 1: {data_1}\n"
            f"📊 Data 2: {data_2}\n"
            f"📊 Data 3: {data_3}\n"
            f"━━━━━━━━━━━━━━━"
        )
        bot.reply_to(message, res_msg, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi Etsy: {str(e)}")

def run_polling():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
