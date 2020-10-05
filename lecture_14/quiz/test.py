import telebot
import shelve
import requests

import config


bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(content_types=['text'])
def get_file_id(message):
    msg = bot.send_message(message.chat.id, "привет")
    bot.up


def download_file(file_id, file_name):
    link = 'https://api.telegram.org/file/bot{}/{}'.format(config.TOKEN, bot.get_file(file_id).file_path)
    to_write = requests.get(link).content
    with open(file_name, "wb") as file:
        file.write(to_write)



if __name__ == '__main__':
    bot.infinity_polling()