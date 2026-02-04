import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
import telegram
from urllib.parse import quote_plus

# ---------------- CONFIGURATION ----------------
username = "amajamajoseph"
password = "desbullyD731950@"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@ajgoldhub.5zwpp39.mongodb.net/ajgold?retryWrites=true&w=majority"

DB_NAME = "ajgold"
COLLECTION_NAME = "news"

TELEGRAM_TOKEN = "8389654198:AAFYia3UhjtzKaVqqdVHEVIgCripZBdM9Xg"
CHAT_ID = "-1003783021892"

NEWS_URL = "https://www.investing.com/news/commodities-news"
# -----------------------------------------------

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Scrape Gold News
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(NEWS_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Example: extract first 5 news items
news_items = soup.select(".textDiv a")[:5]

scraped_news = []
for item in news_items:
    title = item.get_text(strip=True)
    url = "https://www.investing.com" + item.get("href")
    timestamp = datetime.datetime.now()
    
    # Avoid duplicates
    if not collection.find_one({"title": title}):
        collection.insert_one({
            "title": title,
            "url": url,
            "timestamp": timestamp
        })
        scraped_news.append(f"{title}\n{url}")

# Send Telegram Message if there’s news
if scraped_news:
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    message = "🟡 *Today's Gold News* 🟡\n\n" + "\n\n".join(scraped_news)
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
    print("News sent to Telegram!")
else:
    print("No new gold/XAUUSD/metal news today.")
