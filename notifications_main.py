from time import time as get_current_time

import vk_api

from foodsharing_groups import get_foodsharing_groups
from cities import get_city_by_post
from groups_posts import fetch_groups_posts

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

    last_update_time = int(get_current_time())
    while True:
        current_update_time = int(get_current_time())
        foodsharing_groups = get_foodsharing_groups(vk=collector_vk)
        new_posts = fetch_groups_posts(
            [group["id"] for group in foodsharing_groups],
            time_begin=last_update_time, time_end=current_update_time,
            vk=collector_vk
        )
        for post in new_posts:
            process_post(post, bot_vk=bot_vk, collector_vk=collector_vk)
        last_update_time = current_update_time