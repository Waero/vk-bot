#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
import random

import database
from vkapi import *
import sqlite3 as db
from ConfigParser import SafeConfigParser


def worker(user, textfield):
    # Витягуємо в змінні max i min значення для рандому
    config = SafeConfigParser()
    config.read('config.ini')
    max = config.getint('main', 'max')
    min = config.getint('main', 'min')
    # При старті присвоюємо юзерам час очікування, щоб кожен стартанув у різний час
    database.maxRequestSend(user[0])
    sleep = random.randrange(min, max)
    textfield.insert('end', "Юзер № {} налаштований і чекає {} секунд \n".format(user[0], sleep))
    time.sleep(sleep)

    # Отримуємо всіх друзів юзера (тянемо тільки ID). Також ловимо помилку про авторизацією і виводимо її
    try:
        user_friends = getFriendsAndSession(login=user[1], password=user[2])
        sleep2 = random.randrange(min, max)
        textfield.insert('end', 'Юзер № {} зайшов до своїх друзів у нього їх {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                                repr(user_friends[0].__len__()).decode("unicode_escape"),
                                                                                                                sleep2))
        time.sleep(sleep2)
    except Exception as e:
        textfield.insert('end', 'Юзер № {} припинив роботу, причина : {} \n'.format(user[0], e.message))

    # Проходимось по всіх друзях юзера і по його друзях. Основний код
    for uid in user_friends[0]:

        # Відкриваємо профіль друга
        sleep3 = random.randrange(min, max)
        open_friend_profile = getUser(session=user_friends[1], id=uid)
        textfield.insert('end', 'Юзер № {} відкрив профіль друга id= {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                        uid,
                                                                                                        sleep3))
        #textfield.insert('end', repr(open_friend_profile).decode("unicode_escape"))
        time.sleep(sleep3)

        #Витягуємо друзів друга
        friends_from_friend = getFriends(session=user_friends[1], id=uid)
        textfield.insert('end', 'Юзер № {} зайшов до друзів друга id= {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                         uid,
                                                                                                         sleep2))
        time.sleep(sleep2)

        #Знаходимо людей яких у нас ще нема в друзях і віднімаємо тих кому вже відправляли запрос
        mutal_friends = getMutalFriends(session=user_friends[1], id=uid)
        sended_request = getRequests(session=user_friends[1])
        no_friends_yet = set(friends_from_friend) ^ set(mutal_friends) ^ set(sended_request)
        #no_friends_yet = list(set(no_friends_yet))
        textfield.insert('end', 'Юзер № {} знайшов {} не доданих друзів. Він чекає {} секунд \n'.format(user[0],
                                                                                                        len(no_friends_yet),
                                                                                                        sleep))
        time.sleep(sleep)
        # Відкриваємо профіль юзера з людей яких у нас ще нема в друзях
        for no_friendID in no_friends_yet:
            # Перевіряємо чи не перебільшений ліміт на день
            send_and_max_request = database.sendRequest(user[0])
            if send_and_max_request[1] == send_and_max_request[0]:
                textfield.insert('end',
                                 'Юзер № {} припинив роботу. Відправлено максимальну к-сь запитів на день \n'.format(user[0]))
                raise Exception('Stop')
            #if send_and_max_request
            open_user_profile = getUser(session=user_friends[1], id=no_friendID)
            textfield.insert('end', 'Юзер № {} відкрив профіль не друга id= {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                                  no_friendID,
                                                                                                                  sleep2))
            # textfield.insert('end', repr(open_friend_profile).decode("unicode_escape"))
            time.sleep(sleep2)

            # Якщо сторінка друга видалена то vk вертає error. Тут його ловимо і виводимо
            try:
                # Перевіряємо чи користувач активний(тобто заходив у ВК протягом останніх 2х тижнів
                if time.time() - open_user_profile[0]['last_seen']['time'] > 1210000:
                    raise Exception('Користувач не заходив вже більше 2 тижнів')
                # Перевіряємо чи є у нас більше трьох спільних юзерів, якщо є, то додаємо в друзі, якщо ні, то відкриваємо наступного
                mutal = getMutalFriends(session=user_friends[1], id=no_friendID)
                sleep4 = random.randrange(min, max)
                textfield.insert('end',
                                 'Юзер № {} перевіряє чи є більше 3 спільних друзів з id= {}. Він чекає {} секунд \n'.format(
                                     user[0],
                                     no_friendID,
                                     sleep4))
                time.sleep(sleep4)
                # Якщо спільних друзів більше 3 то йдемо далі.
                if mutal.__len__() >= 3:
                    # Перевіряємо чи нема ботів-сторінок в друзях. Якщо є, то не додаємо їх.
                    if [i for i in mutal if i in bots_id] == []:
                        # ловимо капчу якщо буде
                        try:
                            response = addToFriend(session=user_friends[1], id=no_friendID)
                            textfield.insert('end',
                                                 'Юзер № {} відправив заявку в друзі юзеру з id= {}. Він чекає {} секунд \n'.format(
                                                     user[0],
                                                     no_friendID,
                                                     sleep))
                            database.sendRequestCount(user[0])  # Додаємо в каунтер +1
                            time.sleep(sleep)

                        except Exception as e:
                            # ifCaptcha(e=e, session=user_friends[1], id=no_friendID)
                            raise NameError('Потрібно ввести капчу')

                    else:
                        raise Exception('знайдено спільного друга з ботом зі списку')
                else:
                    textfield.insert('end', 'Юзер № {} не знайшов 3 спільних друзів з id= {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                                             no_friendID,
                                                                                                                             sleep3))
                    time.sleep(sleep3)
            except Exception as e:
                if e.__class__ == NameError:
                #if e.message == 'Потрібно ввести капчу':
                    textfield.insert('end', 'Юзер № {} припинив роботу, причина: {} \n'.format(user[0], e.message))
                    raise Exception
                textfield.insert('end', 'Юзер № {} не додав в друзі, причина: {} \n'.format(user[0], e.message))


#  Цю зміннну потрібно щоб перевірити чи ботів сторінок нема у друзях.
bots_id = []


# Метод створює паралельні процеси. Для кожного юзера свій процес
def goWork(textfield):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    for i in cur.execute("SELECT * FROM users WHERE start_work=1;"):
        bots_id.append(i[6])
        t = threading.Thread(target=worker, args=(i,textfield))
        t.start()

    textfield.insert('end',"Всі потоки запущено, програма почала працювати!\n")


# Метод на капчу (поки не імплементований)
def ifCaptcha(e, session, id):
    e.captcha_img
    config = SafeConfigParser()
    config.read('config.ini')
    key = config.get('main', 'key')
    addToFriendCaptcha(session=session, id=id, captcha_sid=e.captcha_sid, captcha_key=key)

