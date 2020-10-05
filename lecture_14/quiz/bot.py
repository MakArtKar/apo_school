import telebot
import random
from telebot import types
import time
import os

import config
import utils
import db_manager

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['setup'])
def set_game_up(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Начинаю настройку игры...")

    quest = dict()
    for file in os.listdir(config.MUSIC_DIRECTORY):
        if file.split('.')[-1] == 'ogg':
            file_id = ''
            with open(config.MUSIC_DIRECTORY + file, 'rb') as audio:
                msg = bot.send_voice(chat_id, audio)
                file_id = msg.voice.file_id
                bot.delete_message(chat_id, msg.message_id)

            key = '.'.join(file.split('.')[:-1])
            quest[key] = [file_id]

    with open(config.MISIC_INFO_FILE) as info:
        for line in info:
            key, right_answer, wrong_answers = line.split('/')
            if key not in quest:
                print("Bad music info file!")
                continue
            quest[key].append(right_answer)
            quest[key].append(wrong_answers)

    table_rows = []
    for value in quest.values():
        table_rows.append(tuple(value))
    db_manager.fill_table(table_rows)

    utils.init_shelve(clear_shelve=True)

    bot.send_message(chat_id, "Игра настроена.")


@bot.message_handler(commands=['game'])
def game(message):
    rows_count = utils.get_rows_count()
    if rows_count == 0:
        bot.send_message(message.chat.id, "Бот не настроен. Выберите команду /setup, чтобы настроить бота.")
        return

    # Выбираем случайный вопрос
    row_id = random.randint(1, rows_count)
    row = db_manager.select_row(row_id)

    # Отправляем вопрос
    markup = utils.generate_markup(row['right_answer'], row['wrong_answers'])
    msg = bot.send_voice(message.chat.id, row['file_id'], reply_markup=markup)

    # Записываем состояние игры для игрока.
    utils.set_user_game(message.chat.id, row['right_answer'])


@bot.message_handler(content_types=['text'])
def check_answer(message):
    # Если функция возвращает None -> Человек не в игре
    answer = utils.get_answer_for_user(message.chat.id)

    if not answer:
        bot.send_message(message.chat.id, 'Чтобы начать игру, выберите команду /game')
    else:
        keyboard_hider = types.ReplyKeyboardRemove()
        if message.text == answer:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id, 'Увы, Вы не угадали. Попробуйте ещё раз!', reply_markup=keyboard_hider)
        # Удаляем юзера из хранилища (игра закончена)
        utils.finish_user_game(message.chat.id)


if __name__ == '__main__':
    utils.init_shelve()
    random.seed()
    bot.infinity_polling()
