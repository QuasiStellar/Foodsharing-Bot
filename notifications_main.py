import time

import vk_api

from cities import get_city_by_post
from newsfeed_posts import fetch_new_posts

from settings import collection_bot_login, collection_bot_password, token


def process_post(post, *, bot_vk, collector_vk):
    city = get_city_by_post(post, vk=collector_vk)
    if city is None:
        return
    # TODO: тут нужно разослать пост всем юзерам с данным городом.
    #       Только не делай тут подключение к базе, лучше передай подключение аргументом
    # TODO: и используй для отправки сообщений bot_vk, а не collector_vk, конечно же
    raise NotImplementedError


def main():
    collector_vk_session = vk_api.VkApi(
        login=collection_bot_login, password=collection_bot_password
    )
    collector_vk_session.auth()
    collector_vk = collector_vk_session.get_api()

    bot_vk_session = vk_api.VkApi(token=token)
    bot_vk = bot_vk_session.get_api()

    last_update_time = int(time.time())
    while True:
        time.sleep(60)
        current_update_time = int(time.time())
        new_posts = fetch_new_posts(
            time_begin=last_update_time, time_end=current_update_time,
            vk=collector_vk
        )
        new_posts = sorted(new_posts, key=lambda post: post["date"])
        for post in new_posts:
            # TODO: try/except
            process_post(post, bot_vk=bot_vk, collector_vk=collector_vk)
        last_update_time = current_update_time


if __name__ == '__main__':
    main()
