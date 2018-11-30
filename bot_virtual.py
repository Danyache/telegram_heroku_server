import math
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import requests
from bs4 import BeautifulSoup
import re
# from PIL import Image
# from io import BytesIO



TOKEN = '633998206:AAG_wQi0DWwUJIGwrZmg-XOubPXu707Z3Dk'
# from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def get_href(film_name):
    words = film_name.split()
    url = 'https://www.google.ru/search?q='
    for word in words:
        url = url + word + '%20'

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    url = url + 'смотреть%20онлайн%20в%20хорошем%20качестве'

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html')
    successor_urls = soup.findAll('div', class_='g')
    links = []
    for i in range(5):
        href = successor_urls[i].find('a').get('href')
        # match = re.search('&sa=U', href)
        # another_match = re.search("https?://", href)
        # n = match.start()
        # m = another_match.start()
        # links.append(successor_urls[i].find('a').get('href')[m:n])
        links.append(href)
    return links

def get_imdb_link(film_name):
    url = "https://www.imdb.com/find?ref_=nv_sr_fn&q="
    words = film_name.split()

    for word in words:
        url = url + word + '+'

    url = url + "&s=all"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html')
    film_url = soup.find('td', class_='result_text').find('a').get('href')
    new_url = "https://www.imdb.com" + film_url
    return new_url

def get_poster(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html')
    # Доделать good quality poster_url = 'https://www.imdb.com' + soup.find('div', class_='poster').a.get('href')
    return soup.find('div', class_='poster').find('img').get('src')

def get_rating(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html')
    return soup.find('div', class_='imdbRating').strong.get('title')

def get_info(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html')
    return soup.find('div', class_='plot_summary').find('div', class_='summary_text').text.replace('\n', ' ').strip()




@dp.message_handler(commands=['start'], commands_prefix='!/')
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nНапиши мне название фильма!")


@dp.message_handler(commands=['help'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне название фильма, а я дам про него информацию и подскажу, где его можно посмотреть!")


@dp.message_handler()
async def film_info(msg: types.Message):
    
    # Тут мы получаем ссылку на то, где посмотреть фильм
    try:
        film_name = msg.text
        answer = get_href(film_name)
        await bot.send_message(msg.from_user.id, 'Посмотреть фильм можно здесь')
        await bot.send_message(msg.from_user.id, answer[0])
        await bot.send_message(msg.from_user.id, 'Если вдруг ссылка нерабочая, то еще можете попробовать посмотреть тут')
        new_films = ''
        for href in answer[1:]:
            new_films = new_films + href + '\n'
        await bot.send_message(msg.from_user.id, new_films)


    except:
        await bot.send_message(msg.from_user.id, 'К сожалению, не могу найти, где посмотреть этот фильм')

    try:
        imdb_link = get_imdb_link(film_name)
    except:
        await bot.send_message(msg.from_user.id, 'К сожалению, не нашел информацию по этому фильму в базе')

    # А вот и описание

    info = get_info(imdb_link)
    await bot.send_message(msg.from_user.id, info)

    # А вот и рейтинг

    rating = get_rating(imdb_link)
    await bot.send_message(msg.from_user.id, rating)

    # А вот и постер

    poster_url = get_poster(imdb_link)

    await bot.send_photo(msg.chat.id, types.InputFile.from_url(poster_url))


if __name__ == '__main__':
    executor.start_polling(dp)
