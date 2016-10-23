#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
import random
from vkapi import *
import sqlite3 as db


def worker(user, textfield):
    # При старті присвоюємо юзерам час очікування, щоб кожен стартанув у різний час
    sleep = random.randrange(1, 10)
    textfield.insert('end', "Юзер № {} налаштований і чекає {} секунд \n".format(user[0], sleep))
    time.sleep(sleep)

    # Отримуємо всіх друзів юзера (тянемо тільки ID)
    user_friends = getFriendsAndSession(login=user[1], password=user[2])
    sleep2 = random.randrange(1, 10)
    textfield.insert('end', 'Юзер № {} зайшов до своїх друзів у нього їх {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                            repr(user_friends[0].__len__()).decode("unicode_escape"),
                                                                                                            sleep2))
    time.sleep(sleep2)

    # randomID - Вибираємо рандомного юзера між 20 і к-сті друзів у юзера
    randomID = random.randrange(20, user_friends[0].__len__())

    # Відкриваємо профіль друга
    open_friend_profile = getUser(session=user_friends[1], id=user_friends[0][randomID])
    textfield.insert('end', 'Юзер № {} відкрив профіль друга id= {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                    user_friends[0][randomID],
                                                                                                    sleep))
    #textfield.insert('end', repr(open_friend_profile).decode("unicode_escape"))
    time.sleep(sleep)

    #Витягуємо друзів друга
    friends_from_friend = getFriends(session=user_friends[1], id=user_friends[0][randomID])
    textfield.insert('end', 'Юзер № {} зайшов до друзів друга id= {}. Він чекає {} секунд \n'.format(user[0],
                                                                                                     user_friends[0][randomID],
                                                                                                     sleep2))
    time.sleep(sleep2)

    #Знаходимо людей яких у нас ще нема в друзях
    mutal_friends = getMutalFriends(session=user_friends[1], id=user_friends[0][randomID])
    no_friends_yet = friends_from_friend + mutal_friends
    no_friends_yet = list(set(no_friends_yet))
    print no_friends_yet
    textfield.insert('end', 'Юзер № {} знайшов {} не доданих друзів. Він чекає {} секунд \n'.format(user[0],
                                                                                                    len(no_friends_yet),
                                                                                                    sleep))
    time.sleep(sleep)


# Метод створює паралельні процеси. Для кожного юзера свій процес
def goWork(textfield):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    for i in cur.execute("SELECT * FROM users;"):
        t = threading.Thread(target=worker, args=(i,textfield))
        t.start()

    textfield.insert('end',"Всі потоки запущено, програма почала працювати!\n")