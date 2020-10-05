import vk
from time import sleep
import config

auth_data_path = "auth.txt"
session_scope = 'wall'
request_delay = 2


def login_to_vk():

    app_id = config.vk_app_id
    login = config.vk_login
    password = config.vk_password

    session = vk.AuthSession(app_id, login, password, scope=session_scope)
    api = vk.API(session, v='5.91', lang='ru', timeout=10)

    sleep(request_delay)

    return api


def get_post_count(api, public_id):
    res = api.wall.get(owner_id=public_id, count=0, offset=0)['count']
    sleep(request_delay)
    return res


def get_posts(api, public_id, offset, count):
    if count < 0 or count > 100:
        raise ValueError("count should be in range [0; 100]")
    if offset < 0:
        raise ValueError("offset should be >= 0")
    try:
        res = api.wall.get(owner_id=public_id, count=count, offset=offset)
        sleep(request_delay)
    except:
        raise

    return res['items']


def get_comments_list(api, post):
    pack_size = 100

    try:
        comment_count = api.wall.getComments(owner_id=post['owner_id'], post_id=post['id'], count=0)['count']

        comment_list = []

        offset = 0
        while len(comment_list) < comment_count:
            comments = api.wall.getComments(owner_id=post['owner_id'], post_id=post['id'],
                                            count=pack_size, sort='asc', offset=offset,
                                            preview_length=0)['items']
            offset = offset + pack_size
            sleep(request_delay)

            for cmt in comments:
                comment_list.append(cmt)
                #print("  ", cmt)

                ans_cnt = cmt['thread']['count']
                for i in range(0, ans_cnt, pack_size):
                    answers = api.wall.getComments(owner_id=post['owner_id'], post_id=post['id'], comment_id=cmt['id'],
                                                   offset=i, count=pack_size, sort='asc', preview_length=0)['items']
                    sleep(request_delay)

                    for ans in answers:
                        comment_list.append(ans)
                        #print("    ", ans)
    except:
        raise

    return comment_list


def answer_to_comment(api, post, comment, text):
    api.wall.createComment(owner_id=post['owner_id'], post_id=post['id'],
                           message=text, reply_to_comment=comment['id'])
    sleep(request_delay)
