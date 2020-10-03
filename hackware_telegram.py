import urllib.parse as urlparse
from urllib.parse import parse_qs
import re
import time
import os

import requests
from bs4 import BeautifulSoup
import telegram
from peewee import *
from playhouse.db_url import connect


def parse_main_page(url):
    html = requests.get(
        url,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.121 Safari/537.36"}
    ).text
    soup = BeautifulSoup(html, features="lxml")
    articles = {}

    for tag in soup.find_all('div', class_=re.compile(r'^featured-box view(t)?$')):
        article_name = tag.a.h3.string
        article_url = tag.a.attrs['href']
        article_id = int(parse_qs(urlparse.urlparse(article_url).query)['p'][0])
        articles[article_id] = article_name

    return articles


if __name__ == "__main__":
    db = connect(os.environ.get("DATABASE_URL") or input("Input DB URL: "))


    class BaseModel(Model):
        class Meta:
            database = db


    class Post(BaseModel):
        id = IntegerField(primary_key=True)
        name = CharField(max_length=255)

        class Meta:
            table_name = "post"


    class EnglishPost(BaseModel):
        id = IntegerField(primary_key=True)
        name = CharField(max_length=255)

        class Meta:
            table_name = "post_english"


    with db:
        db.create_tables([Post, EnglishPost])

    try:
        BOT_TOKEN = os.environ['BOT_TOKEN']
        CHANNEL_ID = int(os.environ['CHANNEL_ID'])
    except KeyError:
        BOT_TOKEN = input("Telegram Bot API token: ")
        CHANNEL_ID = int(input("Telegram channel ID: "))

    bot = telegram.Bot(BOT_TOKEN)


    def check_site(site_url="https://hackware.ru/", model=Post):
        articles = parse_main_page(site_url)
        ids = tuple(articles.keys())
        found_ids = [post.id for post in model.select().where(model.id.in_(ids))]
        new_ids = sorted(list(set(ids) - set(found_ids)))
        for post_id in new_ids:
            post_name = articles[post_id]
            model.create(id=post_id, name=post_name)
            message = f"<b>{post_name}</b>\n{site_url}?p={post_id}"
            bot.send_message(CHANNEL_ID, message, parse_mode="HTML")


    while 1:
        check_site("https://hackware.ru/", Post)
        check_site("https://miloserdov.org/", EnglishPost)
        time.sleep(300)
