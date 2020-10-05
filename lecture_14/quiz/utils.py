import shelve
import db_manager
import config
from telebot import types
from random import shuffle


def init_shelve(clear_shelve=False):
    # Инициализация хранилища в том, что мы записываем туда количество ответов.
    # Если ответы менялись - очистим хранилище, чтобы сбросить все игры.
    rows_count = db_manager.get_table_size()
    mode = 'n' if clear_shelve else 'c'
    with shelve.open(config.SHELVE_NAME, mode) as storage:
        storage['rows_count'] = rows_count
    return rows_count


def get_rows_count():
    with shelve.open(config.SHELVE_NAME) as storage:
        rows_count = storage['rows_count']
    return rows_count


def set_user_game(chat_id, estimated_answer):
    """
    Записываем юзера в игроки и запоминаем, что он должен ответить.
    :param chat_id: id юзера
    :param estimated_answer: правильный ответ (из БД)
    """
    with shelve.open(config.SHELVE_NAME) as storage:
        storage[str(chat_id)] = estimated_answer


def finish_user_game(chat_id):
    """
    Заканчиваем игру текущего пользователя и удаляем правильный ответ из хранилища
    :param chat_id: id юзера
    """
    with shelve.open(config.SHELVE_NAME) as storage:
        del storage[str(chat_id)]


def get_answer_for_user(chat_id):
    """
    Получаем правильный ответ для текущего юзера.
    В случае, если человек просто ввёл какие-то символы, не начав игру, возвращаем None
    :param chat_id: id юзера
    :return: (str) Правильный ответ / None
    """
    with shelve.open(config.SHELVE_NAME) as storage:
        try:
            answer = storage[str(chat_id)]
            return answer
        # Если человек не играет, ничего не возвращаем
        except KeyError:
            return None


def generate_markup(right_answer, wrong_answers):
    """
    Создаем кастомную клавиатуру для выбора ответа
    :param right_answer: Правильный ответ
    :param wrong_answers: Набор неправильных ответов
    :return: Объект кастомной клавиатуры
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    # Склеиваем правильный ответ с неправильными
    all_answers = '{},{}'.format(right_answer, wrong_answers)
    # Создаем лист (массив) и записываем в него все элементы
    list_items = []
    for item in all_answers.split(','):
        list_items.append(item)
    # Хорошенько перемешаем все элементы
    shuffle(list_items)
    # Заполняем разметку перемешанными элементами
    for item in list_items:
        markup.add(item)
    return markup
