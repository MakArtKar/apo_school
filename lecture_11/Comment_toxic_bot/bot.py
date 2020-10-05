import telebot
import config
import time
import random
from telebot import types

import vk_features
import text_processing
from pyaspeller import YandexSpeller


bot = telebot.TeleBot(config.TOKEN)

is_commenting = False
is_setting_up = False

public_id = -57846937  # -196787956
answers = ["Правильно не \"{}\", a \"{}\"!"]

user_data = dict()
api = ""
speller = ""


@bot.message_handler(commands=['start'])
def say_hello(message):
    text = "Введите /settings, чтобы перейти к настройкам, или /go, чтобы начать отвечать на комментарии."
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['settings'])
def setup(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Настройки ответов")
    btn2 = types.KeyboardButton("Выбор паблика")
    markup.add(btn1, btn2)

    msg = bot.send_message(message.chat.id, "Какие настройки вам нужны?", reply_markup=markup)
    bot.register_next_step_handler(msg, choose_setup)


def choose_setup(message):
    if message.text == "Настройки ответов":
        answer_setup(message)
    elif message.text == "Выбор паблика":
        public_setup(message)
    elif message.text == "/stop":
        bot.send_message(message.chat.id, "Выхожу из режима настроек")
        return
    else:
        text = "Такая настройка отсутствует. Выберите вариант на клавиатуре или напишите /stop чтобы выйти из настроек."
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, choose_setup)


def answer_setup(message):
    msg = bot.send_message(message.chat.id, "Добавьте вариант ответа в формате: \"Правильно не {}, a {}\"")
    bot.register_next_step_handler(msg, get_answer)


def get_answer(message):
    global answers
    answers.append(message.text)
    bot.send_message(message.chat.id, "Добавил новый ответ")


def public_setup(message):
    msg = bot.send_message(message.chat.id, "Введите id паблика (начинается с минуса)")
    bot.register_next_step_handler(msg, get_public)


def get_public(message):
    global public_id
    public_id = int(message.text)
    bot.send_message(message.chat.id, "Изменил id паблика")


@bot.message_handler(commands=['go'])
def comment(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Да")
    btn2 = types.KeyboardButton("Нет")
    markup.add(btn1, btn2)

    text = "Начать комментировать с настройками\n\nId паблика: " + str(public_id) + "\n\n Варианты ответов:"
    for ans in answers:
        text += "\n" + ans
    msg = bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(msg, start_comment)


def start_comment(message):
    if message.text == 'Нет':
        bot.send_message(message.chat.id, "Окей")
        return

    bot.send_message(message.chat.id, "Приступаю))")

    global api
    global speller

    try:
        api = vk_features.login_to_vk()
        speller = YandexSpeller()
    except Exception as e:
        bot.send_message(message.chat.id, "Не могу запустить API")
        print("Can't init APIs:", e)
        exit(0)

    bot.send_message(message.chat.id, "Загрузил API")
    print("Successfully logged in!")

    user = message.chat.id
    user_data[user] = {'posts_amount': vk_features.get_post_count(api, public_id), 'posts_cnt': 0,
                       'curr_post': None, 'changes': [], 'changes_cnt': 0}
    ask_permission(message)


def ask_permission(message):
    user = message.chat.id
    data = user_data[user]

    if data['changes_cnt'] >= len(data['changes']):
        data['changes_cnt'] = 0
        bot.send_message(message.chat.id, "Загружаю новый пост...")
        while data['posts_cnt'] < data['posts_amount']:
            data['curr_post'] = vk_features.get_posts(api, public_id, data['posts_cnt'], 1)[0]
            data['posts_cnt'] += 1
            if data['curr_post']['comments']['can_post'] == 1:
                bot.send_message(message.chat.id, "Смотрю, что прокомментировать...")
                comments = vk_features.get_comments_list(api, data['curr_post'])
                data['changes'] = text_processing.get_changes_list(speller, comments)
                break
        else:
            bot.send_message(message.chat.id, "Комментарии закончились :(")
            return

    change = data['changes'][data['changes_cnt']]
    data['changes_cnt'] += 1

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Да")
    btn2 = types.KeyboardButton("Нет")
    markup.add(btn1, btn2)

    text = "Заменяем {} на {}?".format(change[1]['word'], change[1]['s'][0])
    msg = bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(msg, send_comment)


def send_comment(message):
    if message.text == '/stop':
        bot.send_message(message.chat.id, "Заканчиваю комментирование.", reply_markup=types.ReplyKeyboardRemove())
        return

    if message.text == 'Нет':
        bot.send_message(message.chat.id, "Хорошо")
    else:
        user = message.chat.id
        data = user_data[user]

        change = data['changes'][data['changes_cnt']]
        text = answers[random.randint(0, len(answers) - 1)].format(change[1]['word'], change[1]['s'][0])
        vk_features.answer_to_comment(api, data['curr_post'], change[0], text)
        bot.send_message(message.chat.id, "Трололо))")
    ask_permission(message)


if __name__ == '__main__':
    # init
    bot.infinity_polling()