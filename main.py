import random
import pymysql
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from settings import token, group_id, user, password, host


def main():

    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id)

    connection = pymysql.connect(host, user, password, user + '$foodsharing')
    with connection:
        while 'my guitar gently weeps':
            for event in longpoll.listen():
                try:
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        ##### BOT LOGIC #####
                        user_id = event.obj.message['from_id']
                        c = connection.cursor()
                        c.execute('SELECT EXISTS(SELECT id FROM users WHERE id = %s);', (user_id, ))
                        if c.fetchone()[0]:
                            vk.messages.send(user_id=user_id, message='Пользователь уже зарегистрирован.', random_id=get_random_id())
                            c.execute('SELECT id FROM users WHERE id = %s;', (user_id, ))
                        else:
                            vk.messages.send(user_id=user_id, message='Пользователь не зарегистрирован. Регистрация.', random_id=get_random_id())
                            c.execute('INSERT users(id, city, address, priority, rating) VALUES (%s, "", "", "", 0);', (user_id, ))
                            connection.commit()
                        ##### BOT LOGIC #####
                except Exception as e:
                    print(e, flush=True)


print('Start!', flush=True)
main()