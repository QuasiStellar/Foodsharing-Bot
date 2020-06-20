import json


with open("cities.json") as fp:
    _CITIES = tuple(json.load(fp))


def get_cities():
    return _CITIES


def get_city_by_post(post, *, vk):
    group_id = -post["owner_id"]
    group_name = vk.groups.get_by_id(group_id=group_id)[0]["name"]
    cities_included = [city for city in get_cities() if city.lower() in group_name.lower()]
    if len(cities_included) != 1:
        result = None
    else:
        result = cities_included[0]
    return result
