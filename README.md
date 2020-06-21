# Foodsharing-Bot

В данном прототипе реализованы оповещение пользователя о релевантных постах
    и возможность публиковать свои объявления о передаче еды в едином формате.

Стек решения: python, vk_api, mysql, geopy, spacy.


Данный проект состоит из двух программ:
* Программа-интерфейс, реагирующая на сообщения пользователей
* Программа-ретранслятор, отслеживающая новые посты и рассылающая оповещения о новых постах

Программа-ретранслятор в свою очередь использует два аккаунта - аккаунт бота (группа) и аккаунт отслеживания (пользователь).
Аккаунт отслеживания автоматически подписывается на все активные фудшеринг-сообщества, и получает посты прямо из ленты,
после чего находит для каждого поста его город, категорию пищи и адрес, и отсылает каждый пост тем, кому он релевантен.

В программе-интерфейсе пользователь указывает свои город, адрес и предпочтения,
а также имеет возможность публиковать объявления о передаче еды прямо в боте,
после чего они сразу рассылаются всем людям, живущим в том же городе, чьи предпочтения соответствуют категориям из объявления.
Между адресом раздачи и местом жительства пользователя рассчитывается расстояние.
Также реализована частичная защита от спама.
