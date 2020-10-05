from bs4 import BeautifulSoup
import requests
from time import sleep
import keyboard

url = 'https://www.bfm.ru'
weather_url = 'https://yandex.ru/pogoda/moscow'
read = set()


def get_date(link):
    contents = requests.get(link).text

    soup = BeautifulSoup(contents, 'lxml')

    s = soup.find('span', {'class': 'date'})

    if s:
        return s.find(text=True).strip()
    else:
        return None


def get_news_list():
    contents = requests.get(url).text

    soup = BeautifulSoup(contents, 'lxml')

    news = soup.find_all('div', {'class': 'block-news-container'})

    res = []

    for x in news:
        img = x.find('img')
        a = x.find('a')
        title = img['alt']
        image_link = img['src']
        link = url + a['href']

        res.append({'title': title, 'link': link, 'image_link': image_link, 'date': get_date(link)})

    return res


def get_unread_and_update_file(news):
    file = open('data.txt', 'a')

    res = []

    for x in news:
        if x['link'] not in read:
            res.append(x)
            read.add(x['link'])
            print(x['link'], file=file)

    file.close()

    return res


def init_read_set():
    file = open('data.txt', 'r')
    for l in file:
        read.add(l.strip())
    file.close()


def check_news():
    print("Updating...")
    l = get_unread_and_update_file(get_news_list())
    if len(l) == 0:
        print("You have seen everything already\n")
    else:
        print("Here are the posts you haven't seen:")
        for x in l:
            print("Date:", x['date'])
            print("Title:", x['title'])
            print("Image:", x['image_link'])
            print("Link:", x['link'], '\n')


def get_weather():
    contents = requests.get(weather_url).text

    soup = BeautifulSoup(contents, 'lxml')

    res = {}

    cur_temp = soup.find('div', {'class': 'fact__temp-wrap'})
    res['cur_temp'] = cur_temp.find('span', {'class': 'temp__value'}).text.strip()

    res['conditions'] = cur_temp.find('div', {'class': 'link__condition day-anchor i-bem'}).text.strip()

    feels_like = cur_temp.find('div', {'class': 'term term_orient_h fact__feels-like'})
    res['feels_like'] = feels_like.find('span', {'class': 'temp__value'}).text.strip()

    return res


def check_weather():
    weather = get_weather()

    print("Current weather:")
    print("Temperature:", weather['cur_temp'])
    print("Conditions:", weather['conditions'])
    print("Feels like:", weather['feels_like'], '\n')


init_read_set()

keyboard.add_hotkey('alt+shift+1', check_news)
keyboard.add_hotkey('alt+shift+2', check_weather)

keyboard.wait('esc')
