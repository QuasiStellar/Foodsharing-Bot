import pymysql
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from settings import token, group_id, user, password, host
from censor import check_slang
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


categories = {1: 'Выпечка',
                    2: 'Молочное',
                    3: 'Веганское',
                    4: 'Напитки',
                    5: 'Супы',
                    6: 'Мясное',
                    7: 'Бакалея',
                    8: 'Салаты',
                    9: 'Сладости'}

white = VkKeyboardColor.DEFAULT
blue = VkKeyboardColor.PRIMARY
green = VkKeyboardColor.POSITIVE
red = VkKeyboardColor.NEGATIVE


def get_priority_kb(current_priority):
    priority_kb = VkKeyboard(one_time=False)
    priority_kb.add_button(categories[1], color=blue if current_priority >> 0 & 1 else white)
    priority_kb.add_button(categories[2], color=blue if current_priority >> 1 & 1 else white)
    priority_kb.add_button(categories[3], color=blue if current_priority >> 2 & 1 else white)
    priority_kb.add_line()
    priority_kb.add_button(categories[4], color=blue if current_priority >> 3 & 1 else white)
    priority_kb.add_button(categories[5], color=blue if current_priority >> 4 & 1 else white)
    priority_kb.add_button(categories[6], color=blue if current_priority >> 5 & 1 else white)
    priority_kb.add_line()
    priority_kb.add_button(categories[7], color=blue if current_priority >> 6 & 1 else white)
    priority_kb.add_button(categories[8], color=blue if current_priority >> 7 & 1 else white)
    priority_kb.add_button(categories[9], color=blue if current_priority >> 8 & 1 else white)
    priority_kb.add_line()
    priority_kb.add_button('Готово', color=green)
    return priority_kb


def main():

    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id)

    sessions = {}
    requests = {}

    menu_kb = VkKeyboard(one_time=True)
    menu_kb.add_button('Отдать еду', color=green)
    menu_kb.add_line()
    menu_kb.add_button('Выбрать категории', color=white)
    menu_kb.add_line()
    menu_kb.add_button('Изменить город', color=white)
    menu_kb.add_button('Изменить адрес', color=white)

    to_menu_kb = VkKeyboard(one_time=True)
    to_menu_kb.add_button('В меню', color=white)


    while 'my guitar gently weeps':
        for event in longpoll.listen():
            try:
                if event.type == VkBotEventType.MESSAGE_NEW:
                    connection = pymysql.connect(host, user, password, user + '$foodsharing')
                    with connection:

                        ##### BOT LOGIC #####

                        c = connection.cursor()
                        user_id = event.obj.message['from_id']
                        text = event.obj.message['text']
                        if check_slang(text):
                            c.execute('UPDATE users SET address = "ban" WHERE id = %s;', (user_id, ))
                        message_id = event.obj.message['id']
                        c.execute('SELECT EXISTS(SELECT id FROM users WHERE id = %s);', (user_id, ))
                        if c.fetchone()[0]:

                            c.execute('SELECT address FROM users WHERE id = %s;', (user_id, ))
                            if c.fetchone()[0] == 'ban':
                                vk.messages.send(user_id=user_id, message='Вы заблокированы в системе за использование ненормативной лексики.', random_id=get_random_id())
                            elif user_id not in sessions:

                                if text == 'Отдать еду':
                                    if not vk.users.get(user_ids=[user_id], fields=["can_write_private_message"])[0]["can_write_private_message"]:
                                        vk.messages.send(user_id=user_id, message='Необходимо открыть личные сообщения, так с вами можно будет связаться.', random_id=get_random_id(), keyboard=to_menu_kb.get_keyboard())
                                    else:
                                        vk.messages.send(user_id=user_id, message='Укажите адрес раздачи.', random_id=get_random_id(), keyboard=to_menu_kb.get_keyboard())
                                        sessions[user_id] = 'waiting for dist. address'

                                elif text == 'Выбрать категории':
                                    c.execute('SELECT priority FROM users WHERE id = %s;', (user_id, ))
                                    current_priority = c.fetchone()[0]
                                    kb = get_priority_kb(current_priority)
                                    vk.messages.send(user_id=user_id, message='Выберите категории продуктов, уведомления о раздаче которых вы бы хотели получать.', random_id=get_random_id(), keyboard=kb.get_keyboard())
                                    sessions[user_id] = 'waiting for category'

                                elif text == 'Изменить город':
                                    vk.messages.send(user_id=user_id, message='Укажите ваш город. Убедитесь, что название написано правильно.', random_id=get_random_id())
                                    sessions[user_id] = 'waiting for city'

                                elif text == 'Изменить адрес':
                                    vk.messages.send(user_id=user_id, message='Укажите ваш адрес.', random_id=get_random_id())
                                    sessions[user_id] = 'waiting for address'

                                else:
                                    vk.messages.send(user_id=user_id, message='Выберите пункт меню.', random_id=get_random_id(), keyboard=menu_kb.get_keyboard())

                            elif text == 'В меню':
                                del sessions[user_id]
                                vk.messages.send(user_id=user_id, message='Выберите пункт меню.', random_id=get_random_id(), keyboard=menu_kb.get_keyboard())

                            elif sessions[user_id] == 'waiting for city first':
                                c.execute('UPDATE users SET city = %s WHERE id = %s;', (text.lower(), user_id))
                                connection.commit()
                                sessions[user_id] = 'waiting for address first'
                                vk.messages.send(user_id=user_id, message='Город обновлён: ' + text + '\n\nУкажите ваш адрес.', random_id=get_random_id())

                            elif sessions[user_id] == 'waiting for address first':
                                c.execute('UPDATE users SET address = %s WHERE id = %s;', (text.lower(), user_id))
                                connection.commit()
                                sessions[user_id] = 'waiting for category'
                                c.execute('SELECT priority FROM users WHERE id = %s;', (user_id, ))
                                current_priority = c.fetchone()[0]
                                kb = get_priority_kb(current_priority)
                                vk.messages.send(user_id=user_id, message='Адрес обновлён: ' + text + '\n\nВыберите категории продуктов, уведомления о раздаче которых вы бы хотели получать.', random_id=get_random_id(), keyboard=kb.get_keyboard())

                            elif sessions[user_id] == 'waiting for city':
                                c.execute('UPDATE users SET city = %s WHERE id = %s;', (text.lower(), user_id))
                                connection.commit()
                                sessions[user_id] = 'waiting for address'
                                vk.messages.send(user_id=user_id, message='Город обновлён: ' + text + '\n\nУкажите ваш адрес.', random_id=get_random_id())

                            elif sessions[user_id] == 'waiting for address':
                                c.execute('UPDATE users SET address = %s WHERE id = %s;', (text.lower(), user_id))
                                connection.commit()
                                del sessions[user_id]
                                vk.messages.send(user_id=user_id, message='Адрес обновлён: ' + text, random_id=get_random_id(), keyboard=menu_kb.get_keyboard())

                            elif sessions[user_id] == 'waiting for category':
                                if text in categories.values():
                                    c.execute('SELECT priority FROM users WHERE id = %s;', (user_id, ))
                                    current_priority = c.fetchone()[0]
                                    current_priority ^= 1 << list(categories.keys())[list(categories.values()).index(text)] - 1
                                    c.execute('UPDATE users SET priority = %s WHERE id = %s;', (current_priority, user_id))
                                    connection.commit()
                                    vk.messages.send(user_id=user_id, message='Изменения внесены.', random_id=get_random_id(), keyboard=get_priority_kb(current_priority).get_keyboard())
                                elif text == 'Готово':
                                    c.execute('SELECT priority FROM users WHERE id = %s;', (user_id, ))
                                    current_priority = c.fetchone()[0]
                                    if current_priority == 0:
                                        message = 'Ничего не выбрано. Вы не будете получать оповещения о новых раздачах. Чтобы изменить это, выберете несколько категорий.'
                                    else:
                                        message = 'Выбранные категории: '
                                        for i in range(9):
                                            if current_priority >> i & 1:
                                                message += '\n' + categories[i + 1]
                                    vk.messages.send(user_id=user_id, message=message, random_id=get_random_id(), keyboard=to_menu_kb.get_keyboard())

                            elif sessions[user_id] == 'waiting for dist. address':
                                requests[user_id] = {'address': text, 'categories': 0, 'description': '', 'time': ''}
                                sessions[user_id] = 'waiting for dist. categories'
                                vk.messages.send(user_id=user_id, message='Выберите категории отдаваемых продуктов.', random_id=get_random_id(), keyboard=get_priority_kb(0).get_keyboard())

                            elif sessions[user_id] == 'waiting for dist. categories':
                                if text in categories.values():
                                    requests[user_id]['categories'] ^= 1 << list(categories.keys())[list(categories.values()).index(text)] - 1
                                    vk.messages.send(user_id=user_id, message='Изменения внесены.', random_id=get_random_id(), keyboard=get_priority_kb(requests[user_id]['categories']).get_keyboard())
                                elif text == 'Готово':
                                    sessions[user_id] = 'waiting for dist. description'
                                    vk.messages.send(user_id=user_id, message='Опишите отдаваемые продукты.', random_id=get_random_id(), keyboard=to_menu_kb.get_keyboard())

                            elif sessions[user_id] == 'waiting for dist. description':
                                requests[user_id]['description'] = text
                                sessions[user_id] = 'waiting for dist. time'
                                vk.messages.send(user_id=user_id, message='Укажите время раздачи.', random_id=get_random_id(), keyboard=to_menu_kb.get_keyboard())

                            elif sessions[user_id] == 'waiting for dist. time':
                                requests[user_id]['time'] = text
                                sessions[user_id] = 'waiting for dist. image'
                                vk.messages.send(user_id=user_id, message='Прикрепите фотографию продукта.', random_id=get_random_id(), keyboard=to_menu_kb.get_keyboard())

                            elif sessions[user_id] == 'waiting for dist. image':
                                del sessions[user_id]

                                ### DISTRIBUTION HAPPENDS HERE ###

                                c.execute('SELECT city FROM users WHERE id = %s;', (user_id, ))
                                city = c.fetchone()[0]
                                c.execute('SELECT id, address, priority FROM users WHERE city = %s;', (city, ))
                                for recipient in c.fetchall():
                                    geolocator = Nominatim(user_agent="FoodsharingBot")
                                    try:
                                        location1 = geolocator.geocode(city + ' ' + recipient[1])
                                        print(location1)
                                        location2 = geolocator.geocode(city + ' ' + requests[user_id]['address'])
                                        print(location2)
                                        distance = geodesic((location1.latitude, location1.longitude), (location2.latitude, location2.longitude))
                                        distance = round(float(str(distance)[:-3]), 1)
                                    except AttributeError:
                                        distance = False
                                    if recipient[0] != user_id and recipient[2] & requests[user_id]['categories']:
                                        vk.messages.send(user_id=recipient[0], message=requests[user_id]['description'] + '\nАдрес: ' + requests[user_id]['address'] + '\nРасстояние до вас: ' + ((str(distance) + ' км') if distance else 'Не удалось определить :(') + '\nВремя: ' + requests[user_id]['time'] + '\n\nСвязаться с создателем раздачи:', random_id=get_random_id(), forward_messages=[message_id])

                                ### DISTRIBUTION HAPPENDS HERE ###

                                del requests[user_id]
                                vk.messages.send(user_id=user_id, message='Оповещения о раздаче разосланы!', random_id=get_random_id(), keyboard=to_menu_kb.get_keyboard())

                        else:
                            c.execute('INSERT users(id, city, address, priority, rating) VALUES (%s, "", "", 0, 0);', (user_id, ))
                            connection.commit()
                            vk.messages.send(user_id=user_id, message='Укажите ваш город. Убедитесь, что название написано правильно.', random_id=get_random_id())
                            sessions[user_id] = 'waiting for city first'

                        ##### BOT LOGIC #####

            except Exception as e:
                print(e, flush=True)


print('Start!', flush=True)
main()