import urllib.parse as urlparse
from urllib.parse import parse_qs
import re
import time
import json

import requests
from bs4 import BeautifulSoup
import telegram

ENG_ARTICLES = "eng_articles.json"
ARTICLES = "articles.json"


def parse_main_page(url):
    html = requests.get(
        url,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
    ).text
    soup = BeautifulSoup(html, features="lxml")
    articles = {}

    for tag in soup.find_all('div', class_=re.compile(r'^featured-box view(t)?$')):
        article_name = tag.a.h3.string
        article_url = tag.a.attrs['href']
        article_id = parse_qs(urlparse.urlparse(article_url).query)['p'][0]
        articles[article_id] = article_name

    return articles


if __name__ == "__main__":
    try:
        with open("config.json", "r") as f:
            c = json.load(f)
            BOT_TOKEN = c["bot_token"]
            CHANNEL_ID = c["channel_id"]
    except FileNotFoundError:
        print("Please provide the following credentials")
        BOT_TOKEN = input("Telegram Bot API token: ")
        CHANNEL_ID = int(input("Telegram channel ID: "))
        with open("config.json", "w") as f:
            json.dump({"channel_id": CHANNEL_ID, "bot_token": BOT_TOKEN}, f, indent=4)

    bot = telegram.Bot(BOT_TOKEN)
    try:
        with open(ARTICLES, 'r') as f:
            articles = json.load(f)
        with open(ENG_ARTICLES, 'r') as f:
            english_articles = json.load(f)
    except FileNotFoundError:
        articles = parse_main_page("https://hackware.ru/")
        english_articles = parse_main_page("https://miloserdov.org/")

    while 1:
        new_articles = parse_main_page("https://hackware.ru/")
        new_english_articles = parse_main_page("https://miloserdov.org/")
        for article_id, article_name in new_articles.items():
            if article_id not in articles:
                articles[article_id] = article_name
                message = f"<b>{article_name}</b>\nhttps://hackware.ru/?p={article_id}"
                bot.send_message(CHANNEL_ID, message, parse_mode="HTML")
        for article_id, article_name in new_english_articles.items():
            if article_id not in english_articles:
                english_articles[article_id] = article_name
                message = f"<b>{article_name}</b>\nhttps://miloserdov.org/?p={article_id}"
                bot.send_message(CHANNEL_ID, message, parse_mode="HTML")

        with open(ARTICLES, 'w') as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        with open(ENG_ARTICLES, 'w') as f:
            json.dump(english_articles, f, ensure_ascii=False, indent=4)

        time.sleep(300)
