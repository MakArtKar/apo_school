import vk_features
import bot
import random

def delete_special_symbols(text):
    try:
        res = ""
        for c in text:
            if c.isalpha():
                res += c
            elif c == ',' or c == '.' or c == '-':
                res += c
            else:
                res += ' '
        res += '\n'
    except:
        return "Ошибка."

    return res


def make_comments_string(comments):
    res = ""
    for cmt in comments:
        if 'text' not in cmt:
            res += '\n'
            continue
        res += delete_special_symbols(cmt['text'])

    return res


def get_changes_list(speller, comments):
    pack_size = 400

    res = []
    for i in range(0, len(comments), pack_size):
        text = make_comments_string(comments[i:min(len(comments), i + pack_size)])
        changes = speller.spell(text)

        for ch in changes:
            if len(ch['s']) > 0:
                res.append((comments[ch['row'] + i], ch))

    return res


def moderation(api, post, changes_list):
    for ch in changes_list:
        print("       ", ch[1]['word'], "--->", ch[1]['s'][0])
        m = input()
        if m == 'y':
            #text = "Правильно не \"" + ch[1]['word'] + "\", а, \"" + ch[1]['s'][0] + "\"!"
            text = bot.answers[random.randint(0, len(bot.answers))].format(ch[1]['word'], ch[1]['s'][0])
            #print(text)
            vk_features.answer_to_comment(api, post, ch[0], text)
