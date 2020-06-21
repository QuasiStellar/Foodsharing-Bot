import time
import pymysql
import vk_api

from vk_api.utils import get_random_id

from cities import get_city_by_post
from newsfeed_posts import fetch_new_posts

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from settings import collection_bot_login, collection_bot_password, token, host, user, password


def process_post(post, *, bot_vk, collector_vk):
    connection = pymysql.connect(host, user, password, user + '$foodsharing')
    with connection:
        c = connection.cursor()
        city = get_city_by_post(post, vk=collector_vk)
        if city is None:
            return
        c.execute('SELECT id, address, priority FROM users WHERE city = %s;', (city.lower(), ))
        for recipient in c.fetchall():
            geolocator = Nominatim(user_agent="FoodsharingBot")
            try:
                location1 = geolocator.geocode(city + ' ' + recipient[1])
                print(location1)
                location2 = geolocator.geocode(city)# + ' ' + requests[user_id]['address'])
                print(location2)
                distance = geodesic((location1.latitude, location1.longitude), (location2.latitude, location2.longitude))
                distance = round(float(str(distance)[:-3]), 1)
            except AttributeError:
                distance = False
            if True:#recipient[2] & requests[user_id]['categories']:
                bot_vk.messages.send(user_id=recipient[0], message='Новое предложение:', random_id=get_random_id(), attachment='wall%s_%s' % (post['owner_id'], post['id']))


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
            print(post['text'])
            process_post(post, bot_vk=bot_vk, collector_vk=collector_vk)
        last_update_time = current_update_time


if __name__ == '__main__':
    main()
