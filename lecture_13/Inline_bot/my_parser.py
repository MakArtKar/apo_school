import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests


plus_icon = "https://pp.vk.me/c627626/v627626512/2a627/7dlh4RRhd24.jpg"
minus_icon = "https://pp.vk.me/c627626/v627626512/2a635/ILYe7N2n8Zo.jpg"
divide_icon = "https://pp.vk.me/c627626/v627626512/2a620/oAvUk7Awps0.jpg"
multiply_icon = "https://pp.vk.me/c627626/v627626512/2a62e/xqnPMigaP5c.jpg"
error_icon = "https://pp.vk.me/c627626/v627626512/2a67a/ZvTeGq6Mf88.jpg"

koala_id = 'AgACAgIAAxkDAAIFu18Qc3MOtCS-KGlLtWmYXJz6tECTAAJ9rTEb9QN5SKRdBcxRkAGPuojmkS4AAwEAAwIAA20AAx5SBAABGgQ'


smiley_template_url = 'https://ruemoji.ru/assets/img/emoji/1f{}.png'
smiley_nums = ['600', '602', '603', '604', '605', '606', '609', '642', '60a', '61c', '61b', '61d', '60e']


def get_smiley(ind=None):
    if ind == None:
        ind = random.randint(0, len(smiley_nums) - 1)
    return smiley_template_url.format(smiley_nums[ind])


week_best_link = 'https://www.anekdot.ru/release/anekdot/week/'
month_best_link = 'https://www.anekdot.ru/release/anekdot/month/'
year_best_link = 'https://www.anekdot.ru/release/anekdot/year/'

def get_random_link():
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    link = "https://www.anekdot.ru/best/anekdot/{:02d}{:02d}/".format(month, day)
    return link


def parse_jokes_list(link):
    contents = requests.get(link, headers={'User-Agent': UserAgent().chrome}).text
    soup = BeautifulSoup(contents, 'lxml')

    joke_blocks = soup.find_all('div', {'class': 'topicbox'})
    jokes = []
    for block in joke_blocks:
        joke = block.find('div', {'class': 'text'})
        if joke == None:
            continue
        joke = joke.find_all(text=True)

        text = ""
        for line in joke:
            text += line + '\n'
        jokes.append(text)

    return jokes


def get_n_random(n, arr):
    random.shuffle(arr)
    return arr[0:n]
