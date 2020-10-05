import vk_features
import text_processing
from pyaspeller import YandexSpeller

public_id = -57846937  # -196787956

try:
    api = vk_features.login_to_vk()
    speller = YandexSpeller()
except Exception as e:
    print("Can't init APIs:", e)
    exit(0)

print("Successfully logged in!")

post_count = vk_features.get_post_count(api, public_id)

for i in range(post_count):
    post = vk_features.get_posts(api, public_id, i, 1)[0]
    if post['comments']['can_post'] == 1:
        print("Can comment on post", post)
        comments = vk_features.get_comments_list(api, post)
        changes = text_processing.get_changes_list(speller, comments)
        print("  ", len(changes), "changes here!")
        text_processing.moderation(api, post, changes)


