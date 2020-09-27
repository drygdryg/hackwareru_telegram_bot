import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    html = requests.get(
        "https://hackware.ru/",
        headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
    ).text
    soup = BeautifulSoup(html, features="lxml")
    for tag in soup.find_all('div', class_="featured-box viewt"):
        print(tag.a.h3.string)
