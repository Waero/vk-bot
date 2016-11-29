#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
import random

import database
from vkapi import *
import sqlite3 as db
from ConfigParser import SafeConfigParser
from datetime import date, datetime

WORK = True


def worker(user, textfield):
    # Витягуємо в змінні max i min значення для рандому, а також мін спільних друзів
    config = SafeConfigParser()
    config.read('config.ini')
    max = config.getint('main', 'max')
    min = config.getint('main', 'min')
    min_mutal = config.getint('main', 'mutal')
    max_friends = config.getint('main', 'max_friends')
    message = config.get('main', 'message')
    auto_answer = config.getint('main', 'auto_answer')

    # метод максимальних і відправлених реквестів
    requestPerDay(user)
    # При старті присвоюємо юзерам час очікування, щоб кожен стартанув у різний час
    sleep = random.randrange(min, max)
    textfield.insert('end', "Юзер № {} настроен и ждет {} секунд \n".format(user[0], sleep))
    time.sleep(sleep)

    # Отримуємо всіх друзів юзера (тянемо тільки ID). Також ловимо помилку про авторизацію і виводимо її
    try:
        sleep2 = random.randrange(min, max)
        user_friends = getFriendsAndSession(login=user[1], password=user[2])
        #random.shuffle(user_friends[0])  # Перемішуємо друзів, щоб не проходитись завжди від початку списку
        textfield.insert('end', 'Юзер № {} зашел к друзьям у него их {}. Ждет {} секунд \n'.format(user[0],
                                                                                                      repr(user_friends[0].__len__()).decode("unicode_escape"),
                                                                                                      sleep2))
        time.sleep(sleep2)
        textfield.see('end')
    except Exception as e:
        textfield.insert('end', 'Юзер № {} прекратил работу, причина : {} \n'.format(user[0], e.message))
        textfield.see('end')
# Перевіряємо чи не вимкнуто роботу бота
    if WORK == False:
        raise Exception('Stop')
    # Проходимось по всіх друзях юзера і по його друзях. Основний код
    for uid in user_friends[0]:
        # Відкриваємо профіль друга
        sleep3 = random.randrange(min, max)
        open_friend_profile = getUser(session=user_friends[1], id=uid)
        textfield.insert('end', 'Юзер № {} открыл профиль друга id={}. Ждет {} секунд \n'.format(user[0],
                                                                                                    uid,
                                                                                                    sleep3))
        #textfield.insert('end', repr(open_friend_profile).decode("unicode_escape"))
        textfield.see('end')
        time.sleep(sleep3)

        # Витягуємо друзів друга, якщо сторінка заблоковано то вертаємо 0 і йдемо до наступного
        friends_from_friend = getFriends(session=user_friends[1], id=uid)
        if friends_from_friend == 0:
            continue
        textfield.insert('end', 'Юзер № {} зашел к друзьям друга id={}. Ждет {} секунд \n'.format(user[0],
                                                                                                    uid,
                                                                                                    sleep2))
        textfield.see('end')
        time.sleep(sleep2)

        # Знаходимо людей яких у нас ще нема в друзях і віднімаємо тих кому вже відправляли запит
        mutal_friends = getMutalFriends(session=user_friends[1], id=uid)
        sended_request = getRequests(session=user_friends[1])
        friends_without_mutal = set(friends_from_friend) - set(mutal_friends)
        no_friends_yet =  friends_without_mutal - set(sended_request)
        textfield.insert('end', 'Юзер № {} нашел {} потенциальных друзей. Ждет {} секунд \n'.format(user[0],
                                                                                                    len(no_friends_yet),
                                                                                                    sleep))
        textfield.see('end')
        time.sleep(sleep)
        # Відкриваємо профіль юзера з людей яких у нас ще нема в друзях
        for no_friendID in no_friends_yet:
            # Перевіряємо чи не натиснута кнопка СТОП
            if WORK == False:
                raise Exception('Stop')
            # Перевіряємо чи нема не прочитаних повідомлень, якщо є, то відправляємо стандартне повідомлення.
            if auto_answer == 1:
                autoAnswerOnMessage(session=user_friends[1], message=message)
            # Перевіряємо чи не перебільшений ліміт на день
            send_and_max_request = database.sendRequest(user[0])
            if send_and_max_request[1] == send_and_max_request[0]:
                textfield.insert('end',
                                 'Юзер № {} прекратил работу. Отправлено макс к-во запросов на день \n'.format(user[0]))
                textfield.see('end')
                raise Exception('Stop')
            # Відкриваємо профіль користувача
            open_user_profile = getUser(session=user_friends[1], id=no_friendID)
            textfield.insert('end', 'Юзер № {} открыл профиль не друга id={}. Ждет {} секунд \n'.format(user[0],
                                                                                                          no_friendID,
                                                                                                          sleep2))
            # textfield.insert('end', repr(open_friend_profile).decode("unicode_escape"))
            textfield.see('end')
            time.sleep(sleep2)

            # Якщо сторінка друга видалена то vk вертає error. Тут його ловимо і виводимо
            try:
                # Перевіряємо чи користувач активний(тобто заходив у ВК протягом останніх 2х тижнів
                if time.time() - open_user_profile[0]['last_seen']['time'] > 1210000:
                    raise Exception('Пользователь не заходил > 2 недель')
                # Перевіряємо чи у користувача не більше друзів ніж дозволено у нас
                if open_user_profile[0]['counters']['friends'] >= max_friends:
                    raise Exception('У пользователя больше {} друзей'.format(max_friends))
                # Перевіряємо чи є у нас більше мінімальної к-сті (min_mutal) спільних юзерів, якщо є, то додаємо в друзі, якщо ні, то відкриваємо наступного
                mutal = getMutalFriends(session=user_friends[1], id=no_friendID)
                sleep4 = random.randrange(min, max)
                textfield.insert('end',
                                 'Юзер № {} проверяет есть ли > {} общих друзей з id={}. Ждет {} секунд \n'.format(
                                     user[0],
                                     min_mutal,
                                     no_friendID,
                                     sleep4))
                textfield.see('end')
                time.sleep(sleep4)
                # Якщо спільних друзів більше ніж мінімально то йдемо далі.
                if mutal.__len__() >= min_mutal:
                    # Перевіряємо чи нема ботів-сторінок в друзях. Якщо є, то не додаємо їх.
                    if [i for i in mutal if i in bots_id] == []:
                        # Додаємо в друзі або ловимо капчу (якщо буде завершуємо роботу цього бота)
                        try:
                            addToFriend(session=user_friends[1], id=no_friendID)
                            textfield.insert('end',
                                                 'Юзер № {} отправил запрос в друзья юзеру id={}. Ждет {} секунд \n'.format(
                                                     user[0],
                                                     no_friendID,
                                                     sleep))
                            database.sendRequestCount(user[0])  # Додаємо в каунтер +1
                            textfield.see('end')
                            time.sleep(sleep)

                        except Exception as e:
                            # ifCaptcha(e=e, session=user_friends[1], id=no_friendID)
                            raise NameError('Нужно ввести капчу')

                    else:
                        raise Exception('найдено общего друга с ботом в списке')
                else:
                    textfield.insert('end', 'Юзер № {} не нашел {} общих друзей с id={}. Ждет {} секунд \n'.format(user[0],
                                                                                                                        min_mutal,
                                                                                                                        no_friendID,
                                                                                                                        sleep3))
                    textfield.see('end')
                    time.sleep(sleep3)
            except Exception as e:
                if e.__class__ == NameError:
                #if e.message == 'Потрібно ввести капчу':
                    textfield.insert('end', 'Юзер № {} прекратил работу, причина: {} \n'.format(user[0], e.message))
                    textfield.see('end')
                    raise Exception
                textfield.insert('end', 'Юзер № {} не додал в друзья, причина: {} \n'.format(user[0], e.message))
                textfield.see('end')


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

    textfield.insert('end',"Все потоки запущено, Faby начал работать!\n")


# Метод на капчу (поки не імплементований. не потрібно імплементовувати)
def ifCaptcha(e, session, id):
    e.captcha_img
    config = SafeConfigParser()
    config.read('config.ini')
    key = config.get('main', 'key')
    addToFriendCaptcha(session=session, id=id, captcha_sid=e.captcha_sid, captcha_key=key)


# Метод к-сті запросів за день, а також максимальної к-сті
def requestPerDay(user):
    database.maxRequestSend(user[0])
    day = datetime.strptime(user[7], '%Y-%m-%d').date()
    if day != date.today():
        database.updateUserRequest(user[0])


# Метод автоматичної відповіді на повідомлення
def autoAnswerOnMessage(session, message):
    new_messages = getMessages(session)
    if new_messages['count'] != 0:
        for i in new_messages['items']:
            sendMessage(session=session, f_id=i['message']['user_id'], message=message)