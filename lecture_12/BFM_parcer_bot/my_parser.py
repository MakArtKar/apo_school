from bs4 import BeautifulSoup
import requests
from time import sleep
import keyboard

url = 'https://www.bfm.ru'
no_photo_url = 'https://boom-zaim.ru/wp-content/uploads/2019/09/166_trolska-sk-1s.jpg'


def get_news_list():
    contents = requests.get(url).text
    soup = BeautifulSoup(contents, 'lxml')

    news = soup.find_all('div', {'class': 'block-news-container'})
    main_news = soup.find('div', {'class': 'main-container'}).find('a')['href']

    res = [url + main_news]

    got_news = set()
    for x in news:
        link = x.find('a')['href']
        if link not in got_news:
            got_news.add(link)
            res.append(url + link)

    return res

def get_post_data(url):
    contents = requests.get(url).text
    soup = BeautifulSoup(contents, 'lxml')

    img = soup.find('figure', {'class': 'article-figure'})
    if img == None:
        title = "Формат новости не поддерживается"
        text = "Эта новость нетипичная. Пока я не умею такое парсить."
        return {'image_link': no_photo_url, 'title': title, 'date': "", 'text': text}
    else:
        img = img.find('img')['src']
    date = soup.find('span', {'class': 'date'}).find(text=True).strip()
    title = soup.find('h1', {'class': 'news-title'}).find(text=True).strip()
    short_text = soup.find('p', {'class': 'about-article'}).find(text=True).strip()

    return {'image_link': img, 'title': title, 'date': date, 'text': short_text}
