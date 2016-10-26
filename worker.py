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
    maxRequestSend(user[0])
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

        #Знаходимо людей яких у нас ще нема в друзях
        mutal_friends = getMutalFriends(session=user_friends[1], id=uid)
        no_friends_yet = friends_from_friend + mutal_friends
        no_friends_yet = list(set(no_friends_yet))
        textfield.insert('end', 'Юзер № {} знайшов {} не доданих друзів. Він чекає {} секунд \n'.format(user[0],
                                                                                                        len(no_friends_yet),
                                                                                                        sleep))
        time.sleep(sleep)
        # Відкриваємо профіль юзера з людей яких у нас ще нема в друзях
        for no_friendID in no_friends_yet:
            open_user_profile = getUser(session=user_friends[1], id=no_friendID)
            textfield.insert('end', 'Юзер № {} відкрив профіль не друга id= {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                                  no_friendID,
                                                                                                                  sleep2))
            # textfield.insert('end', repr(open_friend_profile).decode("unicode_escape"))
            time.sleep(sleep2)

            # Перевіряємо чи є у нас більше трьох спільних юзерів, якщо є, то додаємо в друзі, якщо ні, то відкриваємо наступного
            sleep4 = random.randrange(min, max)
            textfield.insert('end', 'Юзер № {} перевіряє чи є більше 3 спільних друзів з id= {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                               no_friendID,
                                                                                                               sleep4))
            time.sleep(sleep4)
            # Якщо сторінка удалена то вк вертає ерор. Тут його ловимо і виводимо
            try:
                mutal = getMutalFriends(session=user_friends[1], id=no_friendID)
                if mutal.__len__() >= 3:
                    addToFriend(session=user_friends[1], id=no_friendID)
                    textfield.insert('end',
                                     'Юзер № {} відправив заявку в друзі юзеру з id= {}. Він чекає {} секунд \n'.format(
                                         user[0],
                                         no_friendID,
                                         sleep))
                    database.sendRequestCount(user[0])  # Додаємо в каунтер +1
                    time.sleep(sleep)
                else:
                    textfield.insert('end', 'Юзер № {} не знайшов 3 спільних друзів з id= {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                                             no_friendID,
                                                                                                                             sleep3))
                    time.sleep(sleep3)
            except Exception as e:
                textfield.insert('end', 'Юзер № {} не знайшов спільних друзів, причина : {} \n'.format(user[0], e.message))


# Заносимо в базу Максимальну к-сть заявок друзів які можна кинути
def maxRequestSend(ID):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    ran = random.randrange(35, 45)
    query = "UPDATE users set max_request=? where ID=?"
    cur.execute(query, (ran,ID,))
    con.commit()
    con.close()


# Метод створює паралельні процеси. Для кожного юзера свій процес
def goWork(textfield):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    for i in cur.execute("SELECT * FROM users WHERE start_work=1;"):
        t = threading.Thread(target=worker, args=(i,textfield))
        t.start()

    textfield.insert('end',"Всі потоки запущено, програма почала працювати!\n")