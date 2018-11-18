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

    url = url + 'смотреть%20онлайн%20в%20хорошем%20качестве'

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html')
    successor_urls = soup.findAll('div', class_='g')

    href = successor_urls[0].find('a').get('href')
    match = re.search('&sa=U', href)
    another_match = re.search("https?://", href)
    n = match.start()
    m = another_match.start()

    return successor_urls[0].find('a').get('href')[m:n]

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
    return soup.find('div', class_='poster').find('img').get('src')





@dp.message_handler(commands=['start'], commands_prefix='!/')
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nНапиши мне название фильма!")


@dp.message_handler(commands=['help'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне название фильма, а я дам про него информацию и подскажу, где его можно посмотреть!")


@dp.message_handler()
async def film_info(msg: types.Message):
    film_name = msg.text
    answer = get_href(film_name)

    await bot.send_message(msg.from_user.id, answer)  # msg.text)

    imdb_link = get_imdb_link(film_name)
    poster_url = get_poster(imdb_link)

    await bot.send_photo(msg.chat.id, types.InputFile.from_url(poster_url))


if __name__ == '__main__':
    executor.start_polling(dp)
