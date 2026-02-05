import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
import telegram
from urllib.parse import quote_plus
import schedule
import time

# ---------------- CONFIGURATION ----------------
# MongoDB credentials
username = "amajamajoseph"
password = "desbullyD731950"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@ajgoldhub.5zwpp39.mongodb.net/ajgold?retryWrites=true&w=majority"
DB_NAME = "ajgold"
COLLECTION_NAME = "news"

# Telegram
TELEGRAM_TOKEN = "8389654198:AAFYia3UhjtzKaVqqdVHEVIgCripZBdM9Xg"
CHAT_ID = "-1003783021892"

# News URL
NEWS_URL = "https://www.investing.com/news/commodities-news"

# Keywords for trade-relevant signals
KEYWORDS = ["gold", "xau", "bullish", "buy", "sell", "inflation", "usd", "metal"]

# -----------------------------------------------

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Connect to Telegram
bot = telegram.Bot(token=TELEGRAM_TOKEN)

def run_bot():
    """Scrape news, validate signals, store in MongoDB, and send Telegram messages."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(NEWS_URL, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ERROR fetching news: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    news_items = soup.select(".textDiv a")[:10]  # top 10 news

    scraped_news = []
    for item in news_items:
        title = item.get_text(strip=True)
        url = "https://www.investing.com" + item.get("href")
        timestamp = datetime.datetime.now()

        # Only consider news containing keywords
        if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
            # Avoid duplicates
            if not collection.find_one({"title": title}):
                collection.insert_one({
                    "title": title,
                    "url": url,
                    "timestamp": timestamp
                })
                scraped_news.append(f"{title}\n{url}")

    if scraped_news:
        message = "🟡 *Gold Trade Signals (H1)* 🟡\n\n" + "\n\n".join(scraped_news)
        try:
            bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
            print(f"[{datetime.datetime.now()}] Sent {len(scraped_news)} signals to Telegram.")
        except Exception as e:
            print(f"[{datetime.datetime.now()}] ERROR sending Telegram message: {e}")
    else:
        print(f"[{datetime.datetime.now()}] No new trade-relevant news found.")

    # Logging
    with open("bot_log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: Processed {len(news_items)} items, Sent {len(scraped_news)} signals\n")


# ---------------- SCHEDULER ----------------
# Run the bot at the start of every hour (H1 timeframe)
schedule.every().hour.at(":00").do(run_bot)

print("Gold News Signal Bot running... (H1 signals)")

# Initial run immediately
run_bot()

# Keep the bot running forever
while True:
    schedule.run_pending()
    time.sleep(1)
