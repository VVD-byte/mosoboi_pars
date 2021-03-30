from pars_logic import Parser
import json
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton



bot = Bot('1606013749:AAGBHJjf50kAQTH4MeZxXpdzYxrPILpc3c4')
loop = asyncio.get_event_loop()
dp = Dispatcher(bot, loop=loop)

with open('dat.json', 'r') as t:
    data = json.loads(t.read())

greet_kb = ReplyKeyboardMarkup()
for i in data:
    greet_kb.add(KeyboardButton(i))

@dp.message_handler(commands=['start'])
async def send_welcome(message):
	await bot.send_message(message.from_user.id, "Здравствуйте, задание выполнил Воронин Владимир. Телефон - 89193010473."
                          " Просто выберите бренд, который надо спарсить, все остальное сделает код. Ошибок не должно быть,"
                          "но если что-то пойдет не так, попробуйте спарсить другие бренды. Парсинг займет 20-30 +- секунд,"
                          "надо будет подождать.", reply_markup=greet_kb)


@dp.message_handler()
async def start_pars(message):
    if message.text in data.keys():
        await bot.send_message(message.from_user.id, 'Начали парсить, подождите немного')
        dat = await dp.loop.create_task(Parser(url=data[message.text], name=message.text).pars())
        if dat:
            with open(f'{message.text}.xlsx', 'rb') as t:
                await bot.send_document(message.from_user.id, t)
        else:
            await bot.send_message(message.from_user.id, 'Изините, произошла ошибка, попробуйте позже или спарсите другой бренд')
    else:
        await bot.send_message(message.from_user.id, 'Бренд не найден')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
