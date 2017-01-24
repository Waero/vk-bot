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
    # Витягуємо в змінні max i min значення для рандому, а також інші настройки з config.ini
    config = SafeConfigParser()
    config.read('config.ini')
    max = config.getint('main', 'max')
    min = config.getint('main', 'min')
    min_mutal = config.getint('main', 'mutal')
    max_friends = config.getint('main', 'max_friends')
    message = config.get('main', 'message')
    auto_answer = config.getint('main', 'auto_answer')
    friend_sex = config.getint('main', 'friend_sex')
    auto_post = config.getint('main', 'auto_post')
    upload_photo = config.getint('photo', 'upload_photo')


    # метод максимальних і відправлених реквестів
    requestPerDay(user)
    # При старті присвоюємо юзерам час очікування, щоб кожен стартанув у різний час
    sleep = random.randrange(min, max)
    textfield.insert('end', "Юзер № {} настроен и ждет {} секунд \n".format(user[0], sleep))
    time.sleep(sleep)

    if upload_photo == 1:
        uploadPhoto(user=user, textfield=textfield)

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
                autoAnswerOnMessage(session=user_friends[1], message=message, user_name=user[9])

            # Перевіряємо чи не потрібно постити на стіну, якщо так, то виконуємо метод постингу.
            if auto_post == 1:
                checkIfNeedCopy(session=user_friends[1], user=user)

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
                # Перевіряємо чи користувач активний (тобто заходив у ВК протягом останніх 2х тижнів)
                if time.time() - open_user_profile[0]['last_seen']['time'] > 1210000:
                    raise Exception('Пользователь не заходил > 2 недель')

                # Перевіряємо чи у користувача не більше друзів ніж дозволено у нас
                if open_user_profile[0]['counters']['friends'] >= max_friends:
                    raise Exception('У пользователя > {} друзей'.format(max_friends))

                # Перевіряємо чи користувач потрібної нам статі
                if open_user_profile[0]['sex'] == friend_sex or friend_sex == 3:
                    pass
                else:
                    raise Exception('Пол пользователь не подходит')

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
                            database.addToStatistics(user[9], 'friend')  # Додаємо в статистику
                            time.sleep(sleep)

                        except Exception as e:
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
#def ifCaptcha(e, session, id):
#    e.captcha_img
#    config = SafeConfigParser()
#    config.read('config.ini')
#    key = config.get('main', 'key')
#    addToFriendCaptcha(session=session, id=id, captcha_sid=e.captcha_sid, captcha_key=key)


# Метод к-сті запросів за день, а також максимальної к-сті
def requestPerDay(user):
    database.maxRequestSend(user[0])
    day = datetime.strptime(user[7], '%Y-%m-%d').date()
    if day != date.today():
        database.updateUserRequest(user[0])


# Метод автоматичної відповіді на повідомлення
def autoAnswerOnMessage(session, message, user_name):
    new_messages = getMessages(session)
    if new_messages['count'] != 0:
        for i in new_messages['items']:
            sendMessage(session=session, f_id=i['message']['user_id'], message=message)
            database.addToStatistics(user_name, 'message')  # Додаємо в статистику


# Мотод для копіювання постів
def checkIfNeedCopy(session, user):

    config = SafeConfigParser()
    config.read('config.ini')
    post_date = config.getint('post', 'date')

    # Метод ділиться на дві частини спочатку дивимось, якщо це головна сторінка то виконуємо перший блок, якщо не головна то другий
    # ----- Логіка для головної сторінки -----:
    # В конфіг ми записали дату останнього посту, тут ми перевіряємо чи не зявився новий пост,
    # Якщо зявився то формуємо нові задачі (в базу) для інших сторінок ботів, щоб вони потім зробили пост.
    # ----- Логіка для інших сторінок ботів -----:
    # Перевіряємо чи є у базі завдання на пост, якщо є то постимо.

    if user[10] == 1:
        post = getLastPost(session)
        if post['items'][0]['date'] > post_date:

            attachments = ''
            for p in post['items'][0]['attachments']:
                attachments = attachments + 'photo' + str(p['photo']['owner_id']) + '_' + str(p['photo']['id']) + ','

            # Збарігаємо нове значення дати останнього посту в конфіг файл
            config.set('post', 'date', str(post['items'][0]['date']))
            with open('config.ini', 'w') as f:
                config.write(f)

            # Створюємо завдання в базі даних для інших ботів щоб вони зробили пости
            con = db.connect(database="vkbot")
            cur = con.cursor()
            users = cur.execute("SELECT * FROM users WHERE start_work=1;").fetchall()
            for u in users:
                if u[0] != user[0]: # Щоб не створити завдання основній сторінці
                    cur.execute("insert into tasks (bot_id, text, attachments) values (?, ?, ?)",
                                (u[0], post['items'][0]['text'], attachments))
                    con.commit()
    else:
        con = db.connect(database="vkbot")
        cur = con.cursor()
        task_for_user = (cur.execute("SELECT * FROM tasks WHERE bot_id=?;",(user[0],))).fetchall()
        for task in task_for_user:
            postOnWall(session, task)
            # Видаляємо завдання після посту, щоб бот потім знову це не запостив
            cur.execute("DELETE FROM tasks WHERE id=?;", (task[0],))
            con.commit()
            database.addToStatistics(user[9], 'post')  # Додаємо в статистику


# Мотод для заливки фото
def uploadPhoto(user, textfield):
        config = SafeConfigParser()
        config.read('config.ini')
        dir = config.get('photo', 'upload_dir')
        title = dir.rsplit('/')
        response = getAlbumsTitle(login=user[1], password=user[2])
        session = response[0]
        albums_title = response[1]
        album_id = 0
        for t in albums_title['items']:
            if t['title'].encode('utf-8') != title[-1]:
                continue
            else:
                album_id = t['id']
                break
        if album_id == 0:
            new_album = createNewAlbum(session, title[-1])
            album_id = new_album['id']

        uploadPhotoToAlbum(session, album_id, dir, textfield, user)
