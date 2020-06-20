import time

import vk_api
from vk_api.exceptions import Captcha

from extend_vk_method import extend_vk_method

from settings import collection_bot_login, collection_bot_password


def search_groups(query, *, vk):
    _extended_vk_search_groups = extend_vk_method(vk.groups.search, max_count=1000)
    return list(_extended_vk_search_groups(q=query))


def get_foodsharing_groups(*, vk):
    groups = search_groups(query="Фудшеринг", vk=vk) + search_groups(query="Отдам еду", vk=vk)
    groups = {frozenset(group.items()) for group in groups}
    groups = sorted(map(dict, groups), key=lambda group: group["id"])
    return groups


def get_group_members_count(group_id, *, vk):
    return vk.groups.get_by_id(group_id=group_id, fields=["members_count"])[0]["members_count"]


def main():
    collector_vk_session = vk_api.VkApi(
        login=collection_bot_login, password=collection_bot_password
    )
    collector_vk_session.auth()
    collector_vk = collector_vk_session.get_api()

    foodsharing_groups = get_foodsharing_groups(vk=collector_vk)
    for group in foodsharing_groups:
        group["members_count"] = get_group_members_count(group["id"], vk=collector_vk)
    foodsharing_groups = sorted(
        foodsharing_groups,
        key=lambda group: group["members_count"],
        reverse=True
    )
    sleep_time = 1
    for i, fs_group in enumerate(foodsharing_groups):
        print("Group:", str(i).zfill(3), fs_group["members_count"])
        assert fs_group["id"] > 0
        try:
            collector_vk.wall.get(owner_id=-fs_group["id"], count=3)
        except vk_api.ApiError:
            continue
        success = False
        while not success:
            time.sleep(sleep_time)
            try:
                collector_vk.groups.join(group_id=fs_group["id"])
            except Captcha:
                sleep_time = int(input("Error happened. New sleep time: "))
            else:
                success = True


if __name__ == '__main__':
    main()
