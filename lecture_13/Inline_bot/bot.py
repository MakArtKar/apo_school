import telebot
from telebot import types
import re
import time
import random

import requests
from fake_useragent import UserAgent

import config
import my_parser as mp

bot = telebot.TeleBot(config.TOKEN)

jokes_on_screen = 6


def show_hints(jokes, query):
    offset = int(query.offset) if query.offset else 0
    results = []
    for joke in jokes:
        ind = offset + len(results)
        joke_pre = joke
        if len(joke_pre) > 100:
            joke_pre = joke_pre[:100]

        ans = types.InlineQueryResultArticle(
            id=ind, title="№{}".format(ind + 1),
            description=joke_pre,
            input_message_content=types.InputTextMessageContent(message_text=joke),
            thumb_url=mp.get_smiley()
        )
        results.append(ans)

    bot.answer_inline_query(inline_query_id=query.id, results=results,
                            cache_time=5, next_offset=str(offset + len(results)),
                            switch_pm_text="Войти", switch_pm_parameter='login')


@bot.inline_handler(func=lambda query: len(query.query) == 0)
def show_jokes(query):
    offset = int(query.offset) if query.offset else 0
    if offset >= 100:
        return

    link = mp.get_random_link()
    jokes = mp.parse_jokes_list(link)
    random.shuffle(jokes)

    show_hints(jokes[0:jokes_on_screen], query)


@bot.inline_handler(func=lambda query: re.search(r'([Лл]учшее|[Тт]оп).*[Нн]едел[еию]', query.query))
def show_week_best(query):
    offset = int(query.offset) if query.offset else 0

    link = mp.week_best_link
    jokes = mp.parse_jokes_list(link)

    if offset >= len(jokes):
        return

    delta = min(len(jokes) - offset, jokes_on_screen)
    show_hints(jokes[offset:offset + delta], query)


@bot.inline_handler(func=lambda query: re.search(r'([Лл]учшее|[Тт]оп).*[Мм]есяц([ае]?)', query.query))
def show_month_best(query):
    offset = int(query.offset) if query.offset else 0

    link = mp.month_best_link
    jokes = mp.parse_jokes_list(link)

    if offset >= len(jokes):
        return

    delta = min(len(jokes) - offset, jokes_on_screen)
    show_hints(jokes[offset:offset + delta], query)


@bot.message_handler(commands=['start'])
def process_start(message):
    cmd = message.text.split()
    if len(cmd) > 1 and cmd[1] == 'login':
        login(message)
    else:
        get_started(message)


def login(message):
    text = "Войдите в аккаунт анекдот.ру, чтобы анекдоты подбирались под ваши предпочтения.\n\n"\
           "Для этого отправьте ваш номер телефона."
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("Отправить контакт", request_contact=True)
    markup.add(btn)

    msg = bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(msg, process_contact)


def process_contact(message):
    msg = bot.send_message(message.chat.id, "Контакт получен. Авторизуюсь...")
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(2)
    bot.edit_message_text("Авторизация пройдена", msg.chat.id, msg.message_id)

    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Вернуться в исходный чат.", switch_inline_query="")
    markup.add(btn)

    msg = bot.send_message(message.chat.id, "Возвращаю вас обратно...", reply_markup=markup)


def get_started(message):
    text = "Я бот, который может подсказать анекдот.\n\n"\
           "Нажмите на одну из кнопок, чтобы узнать, как мной пользоваться."
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("Выбрать анекдот из лучших", switch_inline_query="")
    btn2 = types.InlineKeyboardButton("Выбрать анекдот из лучших за неделю",
                                      switch_inline_query="лучшее за неделю")
    btn3 = types.InlineKeyboardButton("Выбрать анекдот из лучших за месяц",
                                      switch_inline_query="лучшее за месяц")
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, text, reply_markup=markup)


if __name__ == '__main__':
    bot.infinity_polling()