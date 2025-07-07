import os
import requests
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet_data(sheet_url):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).sheet1
    return sheet.get_all_records()

def categorize_products(products):
    today = datetime.datetime.now().date()
    categorized = {"🟥": [], "🟧": [], "🟨": [], "🟩": []}
    for product in products:
        try:
            skt_date = datetime.datetime.strptime(product["SKT"], "%d.%m.%Y").date()
            kalan = (skt_date - today).days
            text = f'{product["Ürün"]} – {kalan} gün kaldı ({product["Raf"]})'
            if kalan < 1:
                categorized["🟥"].append(text.replace("– -1 gün", "– BUGÜN SON"))
            elif kalan <= 3:
                categorized["🟧"].append(text)
            elif kalan <= 7:
                categorized["🟨"].append(text)
            else:
                categorized["🟩"].append(text)
        except:
            continue
    return categorized

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, data=payload)

def main():
    SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    products = get_sheet_data(SHEET_URL)
    categorized = categorize_products(products)

    date_str = datetime.datetime.now().strftime("%d %B %Y")
    message = f"📦 SKT Uyarısı – {date_str}
"
    for key in ["🟥", "🟧", "🟨", "🟩"]:
        for line in categorized[key]:
            message += f"{key} {line}
"

    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)

if __name__ == "__main__":
    main()
