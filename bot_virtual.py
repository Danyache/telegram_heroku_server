import math
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import requests
from bs4 import BeautifulSoup
import re
# from PIL import Image
# from io import BytesIO
last_film = {}
imdb_links = {}

TOKEN = '633998206:AAG_wQi0DWwUJIGwrZmg-XOubPXu707Z3Dk'
# from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def get_href(film_name):
    words = film_name.split()
    url = 'https://www.google.ru/search?q='
    for word in words:
        url = url + word + '%20'

    headers = {'User-Agent': 'Chrome/70.0.3538.77 Safari/537.36'}
    url = url + 'смотреть%20онлайн%20в%20хорошем%20качестве'

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html')
    successor_urls = soup.findAll('div', class_='g')
    links = []
    k = 0
    i = 0
    while k<5:
        href = successor_urls[i].find('a').get('href')
        if ("smotri-filmi" not in href) and ("hdrezka.ag" not in href):
            match = re.search('&sa=U', href)
            another_match = re.search("https?://", href)
            n = match.start()
            m = another_match.start()
            links.append(successor_urls[i].find('a').get('href')[m:n])
            k += 1
        # links.append(href)
        i += 1
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

@dp.message_handler(commands=['rating'], commands_prefix='!/')
async def process_start_command(message: types.Message):
    
    # try:
    global last_film
    try:
        film_name = last_film[message.chat.id]
    except:
        await message.reply("Ты еще не указал название ни одного фильма :(")
    try:
        imdb_link = get_imdb_link(film_name)
    except:
        await bot.send_message(message.from_user.id, 'К сожалению, не нашел информацию по этому фильму в базе')

    rating = get_rating(imdb_link)
    await bot.send_message(message.from_user.id, rating)
    

@dp.message_handler(commands=['poster'], commands_prefix='!/')
async def process_start_command(message: types.Message):
    try:
        global last_film
        film_name = last_film[message.chat.id]
        try:
            imdb_link = get_imdb_link(film_name)
        except:
            await bot.send_message(message.from_user.id, 'К сожалению, не нашел информацию по этому фильму в базе')
        poster_url = get_poster(imdb_link)
        await bot.send_photo(message.chat.id, types.InputFile.from_url(poster_url))
    except:
        await message.reply("Ты еще не указал название ни одного фильма :(")

@dp.message_handler(commands=['watch', commands_prefix='!/'])
async def process_start_command(message: types.Message):
    try:
        film_name = last_film[message.chat.id]
    except:
        pass
    try:
        imdb_link = get_imdb_link(film_name)
    except:
        pass

    try:
        answer = get_href(film_name)
        # await bot.send_message(msg.from_user.id, 'Посмотреть фильм можно здесь')
        # await bot.send_message(msg.from_user.id, answer[0])
        await bot.send_message(msg.from_user.id, 'Если вдруг ссылка была нерабочая, то еще можете попробовать посмотреть тут')
        new_films = ''
        for href in answer[1:]:
            new_films = new_films + href + '\n'
        await bot.send_message(msg.from_user.id, new_films)
    except:
        await bot.send_message(msg.from_user.id, 'К сожалению, не могу найти, где посмотреть этот фильм')

@dp.message_handler()
async def film_info(msg: types.Message):
    # Тут мы получаем ссылку на то, где посмотреть фильм
    global last_film
    film_name = msg.text
    last_film[msg.chat.id] = film_name
    # try:
    #     answer = get_href(film_name)
    #     await bot.send_message(msg.from_user.id, 'Посмотреть фильм можно здесь')
    #     await bot.send_message(msg.from_user.id, answer[0])
    #     # await bot.send_message(msg.from_user.id, 'Если вдруг ссылка нерабочая, то еще можете попробовать посмотреть тут')
    #     # new_films = ''
    #     # for href in answer[1:]:
    #     #     new_films = new_films + href + '\n'
    #     # await bot.send_message(msg.from_user.id, new_films)
    # except:
    #     await bot.send_message(msg.from_user.id, 'К сожалению, не могу найти, где посмотреть этот фильм')

    try:
        imdb_link = get_imdb_link(film_name)
    except:
        await bot.send_message(msg.from_user.id, 'К сожалению, не нашел информацию по этому фильму в базе')

    # А вот и описание

    info = get_info(imdb_link)
    await bot.send_message(msg.from_user.id, info)
    # А вот и рейтинг

    # rating = get_rating(imdb_link)
    # await bot.send_message(msg.from_user.id, rating)


    # А вот и постер

    poster_url = get_poster(imdb_link)

    await bot.send_photo(msg.chat.id, types.InputFile.from_url(poster_url))

    # Где посмотреть

    try:
        answer = get_href(film_name)
        await bot.send_message(msg.from_user.id, 'Посмотреть фильм можно здесь')
        await bot.send_message(msg.from_user.id, answer[0])
        # await bot.send_message(msg.from_user.id, 'Если вдруг ссылка нерабочая, то еще можете попробовать посмотреть тут')
        # new_films = ''
        # for href in answer[1:]:
        #     new_films = new_films + href + '\n'
        # await bot.send_message(msg.from_user.id, new_films)
    except:
        await bot.send_message(msg.from_user.id, 'К сожалению, не могу найти, где посмотреть этот фильм')


if __name__ == '__main__':
    executor.start_polling(dp)
