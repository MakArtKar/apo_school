import telebot
from telebot import types
from time import time
import shelve

import config


bot = telebot.TeleBot(config.TOKEN)
channel_name = '@apo_test_channel'


@bot.message_handler(commands=['poll'], func=lambda message: message.chat.type == 'private')
def ask_for_poll(message):
    msg = bot.send_message(message.chat.id, "Отправьте мне опрос, который хотите отослать в канал")
    bot.register_next_step_handler(msg, send_poll)


def send_poll(message):
    p = message.poll
    options = [option.text for option in
               p.options]

    bot.send_poll(channel_name, p.question, options, is_anonymous=p.is_anonymous,
                  type=p.type, allows_multiple_answers=p.allows_multiple_answers,
                  correct_option_id=p.correct_option_id, explanation=p.explanation)


@bot.message_handler(content_types=['new_chat_members'])
def add_member(message):
    with shelve.open('members') as members:
        for user in message.new_chat_members:
            key = "{} {}".format(message.chat.id, user.id)
            if key in members:
                info = members[key]
                info['state'] = 'in_group'
                members[key] = info
            else:
                members[key] = {'state': 'in_group', 'bans': 0}


@bot.message_handler(content_types=['left_chat_member'])
def delete_member(message):
    with shelve.open('members') as members:
        key = "{} {}".format(message.chat.id, message.left_chat_member.id)
        if key in members:
            info = members[key]
            info['state'] = 'not_in_group'
            members[key] = info


@bot.message_handler(commands=['stats'], func=lambda message: message.chat.type == 'supergroup')
def print_chat_members(message):
    text = "Статистика по участникам группы:\n\n"
    with shelve.open('members') as members:
        for user_id, info in members.items():
            user_id = int(user_id.split()[1])
            if info['state'] == 'not_in_group':
                continue
            nick = bot.get_chat_member(message.chat.id, user_id).user.username
            text += "@{} - {} банов.\n".format(nick, info['bans'])
    bot.send_message(message.chat.id, text)


def add_ban(chat_id, user_id, delta=1):
    with shelve.open('members') as members:
        key = "{} {}".format(chat_id, user_id)
        if key in members:

            info = members[key]
            info['bans'] += delta
            members[key] = info


# Определение языка и банк ответов
def get_language(lang_code):
    # Иногда language_code может быть None
    if not lang_code:
        return "en"

    lang_code = lang_code.split("-")[0]
    if lang_code == "ru":
        return "ru"
    else:
        return "en"


messages = {
    "ru": {
        "restrict_msg":
            "Вам запрещено отправлять сюда сообщения в течение 10 минут. Причина - чрезмерная любовь к BMW.",
        "ban_msg":
            "Участник @{} заблокирован. Причина - распространение спама."
    },
    "en": {
        "restrict_msg":
            "You're not allowed to send messages here for 10 minutes. The reason is excessive love for BMW.",
        "ban_msg":
            "@{} is kicked out of the chat. The reason is the spread of spam."
    }
}

# Удаляем сообщения с ссылками и баним их отправителей
@bot.message_handler(func=lambda message: message.entities is not None and message.chat.type == 'supergroup')
def ban_member(message):
    links = []
    for entity in message.entities:
        if entity.type == "url":
            links.append(message.text[entity.offset : entity.offset + entity.length])
        elif entity.type == "text_link":
            links.append(entity.url)

    if len(links) == 0:
        return

    add_ban(message.chat.id, message.from_user.id)
    post_to_channel(message, 'ban', links)
    bot.delete_message(message.chat.id, message.message_id)
    #bot.kick_chat_member(message.chat.id, message.from_user.id, until_date=time() + 24 * 60 * 60)
    text = messages[get_language(message.from_user.language_code)]['ban_msg']
    bot.send_message(message.chat.id, text.format(message.from_user.username))


# Выдаём Read-only за определённые фразы
restricted_messages = ["bmw лучшая", "я люблю bmw", "bmw is the best", "I love bmw"]


def check_for_restricted(text):
    text = text.lower()
    for pattern in restricted_messages:
        if pattern in text:
            return True
    return False


@bot.message_handler(content_types=['text'],
                     func=lambda message: check_for_restricted(message.text)
                                          and message.chat.type == 'supergroup')
def restrict_member(message):
    add_ban(message.chat.id, message.from_user.id)
    post_to_channel(message, 'restrict')
    #bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time() + 600)
    text = messages[get_language(message.from_user.language_code)]['restrict_msg']
    bot.send_message(message.chat.id, text, reply_to_message_id=message.message_id)


# Постим кейс в канал
emoji = {
    'like': b'\xf0\x9f\x91\x8d'.decode('UTF-8'),
    'dislike': b'\xf0\x9f\x91\x8e'.decode('UTF-8')

}


def post_to_channel(message, punish_type, issues=None):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text=emoji['like'] + ' 0', callback_data='like 0 0')
    btn2 = types.InlineKeyboardButton(text=emoji['dislike'] + ' 0', callback_data='dislike 0 0')
    markup.add(btn1, btn2)

    if punish_type == 'ban':
        text = "@{} заблокирован в чате за распространение следующих спам-ссылок:\n".format(
            message.from_user.username)
        for link in issues:
            text += '       * ' + link + '\n'
        text += "\nТак будет с каждым!"
        msg = bot.send_message(channel_name, text, reply_markup=markup)
    else:
        text = "@{} получил ограничение на отправку сообщений в чат за это сообщение:".format(
            message.from_user.username)
        msg = bot.send_message(channel_name, text, reply_markup=markup)
        bot.forward_message(channel_name, message.chat.id, message.message_id)


# Реагируем на нажатие кнопки
@bot.callback_query_handler(func=lambda call: 'like' in call.data or 'dislike' in call.data)
def update_markup(call):
    # Получаем старое и новое количество лайков и дизлайков
    curr_type, old_likes, old_dislikes = call.data.split()
    old_likes = int(old_likes)
    old_dislikes = int(old_dislikes)
    likes, dislikes = get_score(call)

    # Реагируем на кнопку
    if likes <= old_likes and dislikes <= old_dislikes:
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Вы отозвали свою реакцию.")
    else:
        if likes > old_likes:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Вы лайкнули пост.")
        else:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Вы дизлайкнули пост.")

    # Обновляем кнопки
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='{} {}'.format(emoji['like'], likes),
                                      callback_data='like {} {}'.format(likes, dislikes))
    btn2 = types.InlineKeyboardButton(text='{} {}'.format(emoji['dislike'], dislikes),
                                      callback_data='dislike {} {}'.format(likes, dislikes))
    markup.add(btn1, btn2)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


# Получаем новое состояние лайков и дизлайков после нажатия на кнопку
def get_score(call):
    with shelve.open('score') as score:
        key = '{} {} {}'.format(call.message.chat.id, call.message.message_id, call.from_user.id)

        curr_type, likes, dislikes = call.data.split()
        likes = int(likes)
        dislikes = int(dislikes)

        old_likes = likes
        old_dislikes = dislikes

        if key not in score:
            score[key] = curr_type
            if curr_type == 'like':
                likes += 1
            else:
                dislikes += 1
        else:
            if curr_type == score[key]:
                del score[key]
                if curr_type == 'like':
                    likes -= 1
                else:
                    dislikes -= 1
            else:
                score[key] = curr_type
                if curr_type == 'like':
                    likes += 1
                    dislikes -= 1
                else:
                    dislikes += 1
                    likes -= 1

    return likes, dislikes



if __name__ == "__main__":
    bot.infinity_polling()
