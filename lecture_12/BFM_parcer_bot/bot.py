import telebot
from telebot import types
import requests

import config
import my_parser


bot = telebot.TeleBot(config.TOKEN)
user_data = dict()


@bot.message_handler(commands=['start'])
def say_hello(message):
    text = "Нажмите /getnews, чтобы посмотреть последние новости."
    bot.send_message(message.chat.id, text)


def get_news_post(news, index):
    link = news[index]
    data = my_parser.get_post_data(link)

    image = requests.get(data['image_link']).content
    text = "<b>{}</b>\n<i>{}</i>\n\n{}".format(data['title'], data['date'], data['text'])

    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Назад", callback_data="backward")
    btn2 = types.InlineKeyboardButton(text="Вперед", callback_data="forward")
    btn3 = types.InlineKeyboardButton(text="Читать в источнике", url=link)
    if index == 0:
        keyboard.row(btn2)
    elif index + 1 == len(news):
        keyboard.row(btn1)
    else:
        keyboard.row(btn1, btn2)
    keyboard.row(btn3)

    return {'image': image, 'text': text, 'keyboard': keyboard}


@bot.message_handler(commands=['getnews'])
def get_news(message):
    bot.send_message(message.chat.id, "Загружаю новости...")
    news = my_parser.get_news_list()

    if len(news) == 0:
        bot.send_message(message.chat.id, "Нет свежих новостей :(")
        return

    global user_data
    user = message.chat.id

    if user in user_data:
        keyboard = types.InlineKeyboardMarkup()
        bot.edit_message_reply_markup(message.chat.id, user_data[user]['last_message'].message_id, reply_markup=keyboard)

    post = get_news_post(news, 0)
    msg = bot.send_photo(message.chat.id, post['image'], post['text'], parse_mode="HTML", reply_markup=post['keyboard'])

    user_data[message.chat.id] = {'news': news, 'index': 0, 'last_message': msg}


@bot.callback_query_handler(func=lambda call: call.data == 'backward' or call.data == 'forward')
def callback_processing(call):
    global user_data
    user = call.message.chat.id
    if call.data == "backward":
        user_data[user]['index'] -= 1
    else:
        user_data[user]['index'] += 1

    post = get_news_post(user_data[user]['news'], user_data[user]['index'])
    bot.edit_message_media(media=types.InputMedia(type='photo', media=post['image'], caption=post['text'],
                        parse_mode='HTML'), chat_id=call.message.chat.id, message_id=call.message.message_id,
                        reply_markup=post['keyboard'])


if __name__ == '__main__':
    bot.infinity_polling()