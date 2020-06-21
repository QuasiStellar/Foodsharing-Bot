from collections import Counter
import json

from vk_api import ApiError


_MAX_FRIENDS_COUNT = 10_000

with open("cities.json") as fp:
    _CITIES = tuple(json.load(fp))


def get_cities():
    return _CITIES


def try_identify_user_city(user_id, *, vk):
    get_city = lambda user: \
        user["city"]["title"] if "city" in user.keys() else None
    user_data = vk.users.get(user_ids=[user_id], fields=["city"])[0]
    specified_user_city = get_city(user_data)
    try:
        friends = vk.friends.get(
            user_id=user_id, fields=["city"], count=_MAX_FRIENDS_COUNT
        )["items"]
    except ApiError:
        result_city = specified_user_city
    else:
        friends_cities_counter = Counter(map(get_city, friends))
        if None in friends_cities_counter.keys():
            del friends_cities_counter[None]
        most_common = friends_cities_counter.most_common(2)
        most_common = [city for city, count in most_common]
        if specified_user_city in most_common:
            result_city = specified_user_city
        elif len(most_common) != 0:
            result_city = most_common[0]
        else:
            result_city = specified_user_city
    return result_city


def get_city_by_post(post, *, vk):
    if post["owner_id"] >= 0:
        raise ValueError("post must be on group's wall")
    group_id = -post["owner_id"]
    group_name = vk.groups.get_by_id(group_id=group_id)[0]["name"]
    cities_included = [city for city in get_cities() if city.lower() in group_name.lower()]
    if len(cities_included) == 1:
        result_city = cities_included[0]
    else:
        if "from_id" in post.keys() and post["from_id"] > 0:
            author_id = post["from_id"]
        elif "signer_id" in post.keys():
            author_id = post["signer_id"]
        else:
            author_id = None
        if author_id is not None:
            result_city = try_identify_user_city(author_id, vk=vk)
        else:
            result_city = None
    return result_city
