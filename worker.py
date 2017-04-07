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
lock = threading.Lock()


class BotLogic:
    def __init__(self, user, textfield):
        self.user = list(user)
        self.user[9] = self.user[9].encode('utf8')
        self.textfield = textfield
        self.for_invite = []  # Для запрошунь в групу ініціалізуємо змінну
        # Витягуємо в змінні настройки з config.ini
        config = SafeConfigParser()
        config.read('config.ini')
        self.max = config.getint('main', 'max')
        self.min = config.getint('main', 'min')
        self.min_mutal = config.getint('main', 'mutal')
        self.max_friends = config.getint('main', 'max_friends')
        self.message = config.get('main', 'message')
        self.auto_answer = config.getint('main', 'auto_answer')
        self.friend_sex = config.getint('main', 'friend_sex')
        self.auto_post = config.getint('main', 'auto_post')
        self.upload_photo = config.getint('photo', 'upload_photo')
        self.suggested_type = config.getint('main', 'suggested_type')
        self.invite_to_group_id = config.getint('group', 'invite_in_group')
        self.add_to_friend = config.getint('main', 'add_to_friend')

    # Логіка поведінки бота
    def worker(self):

        # Метод максимальних і відправлених реквестів
        lock.acquire()
        self.requestPerDay()
        # При старті присвоюємо юзерам час очікування, щоб кожен стартанув у різний час
        sleep = random.randrange(self.min, self.max)
        self.textfield.insert('end', "{} - настроен и ждет {} секунд\n".format(self.user[9], sleep))
        lock.release()
        time.sleep(sleep)

        if self.upload_photo == 1:
            self.uploadPhoto()

        while WORK:
            lock.acquire()
            self.user_friends = self.getSessionAndFriend()
            lock.release()
            accept_friend(self.user_friends[1])
            # Перевіряємо чи не вимкнуто роботу бота
            if not WORK:
                raise Exception('Stop')

            # Перевіряємо чи будемо додавати в друзі
            if self.add_to_friend == 1:
                self.inviteToFriend()

            # Перевіряємо чи нема не прочитаних повідомлень, якщо є, то відправляємо стандартне повідомлення.
            if self.auto_answer == 1:
                sleep = random.randrange(self.min, self.max)
                lock.acquire()
                self.textfield.insert('end', '{} - проверяет сообщения. Ждет {} секунд\n'.format(self.user[9], sleep))
                self.textfield.see('end')
                lock.release()
                time.sleep(sleep)
                self.autoAnswerOnMessage()
            # Перевіряємо чи не потрібно постити на стіну, якщо так, то виконуємо метод постингу.
            if self.auto_post == 1:
                sleep = random.randrange(self.min, self.max)
                lock.acquire()
                self.textfield.insert('end',
                                      '{} - проверяет стену на постинг. Ждет {} секунд\n'.format(self.user[9], sleep))
                self.textfield.see('end')
                lock.release()
                time.sleep(sleep)
                self.checkIfNeedCopy()

                # Перевіряємо чи не потрібно запрошувати в групу, якщо так, то виконуємо метод запрошення.
            if self.invite_to_group_id != 0:
                sleep = random.randrange(self.min, self.max)
                lock.acquire()
                self.textfield.insert('end',
                                      '{} - готовит приглашение в групу. Ждет {} секунд\n'.format(self.user[9], sleep))
                self.textfield.see('end')
                lock.release()
                time.sleep(sleep)
                self.inviteToGroup()

    def inviteToFriend(self):
        # ------------Дивимось по якому принципу будемо додавати друзів  -------------#
        if self.suggested_type == 1:
            lock.acquire()
            no_friends_yet = self.getSuggestedFriends()
            lock.release()
            self.addNoFriendsYet(no_friends_yet)
        else:
            bot_friend = set(self.user_friends[0]['items']) - set(bots_id)
            bot_friend = list(bot_friend)
            counts = 0
            while len(bot_friend) > counts:
                lock.acquire()
                data = get_candidate(session=self.user_friends[1], bot_friend=bot_friend[counts:counts + 5], max_friends=self.max_friends)
                lock.release()
                counts += 5
                sleep = random.randrange(1, 5)

                friend_profile = data[3]
                friend_name = friend_profile[0]['first_name'].encode('utf8') + ' ' + friend_profile[0]['last_name'].encode('utf8')
                lock.acquire()
                self.textfield.insert('end', '{} - зашел к друзьям друга {}. Ждет {} секунд\n'.format(self.user[9],
                                                                                                       friend_name,
                                                                                                       sleep))
                self.textfield.see('end')
                lock.release()
                time.sleep(sleep)

                # Знаходимо людей яких у нас ще нема в друзях і вісіюємо тих кому вже відправляли запит, і тих хто у нас у спільних
                profiles = data[0]
                mutal_friends = data[1]
                sended_request = data[2]
                no_friends_yet = []
                for i in profiles:
                    if i['id'] not in mutal_friends:
                        if i['id'] not in sended_request:
                            if i['id'] not in bots_id:
                                no_friends_yet.append(i)

                candidates_in_friends = []

                # + Відсіюємо тих хто нам не підходить по профайлу
                for t in no_friends_yet:
                    if 'deactivated' in t: continue
                    if t['blacklisted'] == 1: continue
                    if time.time() - t['last_seen']['time'] > 1210000: continue
                    # Перевіряємо чи користувач потрібної нам статі
                    if t['sex'] == self.friend_sex or self.friend_sex == 3:
                        pass
                    else:
                        continue
                    if t['id'] == self.user[6]: continue  # щоб сам себе не додавав (про всяк випадок)
                    candidates_in_friends.append(t['id'])

                self.addNoFriendsYet(candidates_in_friends)

    # Метод додавання друзів
    def addNoFriendsYet(self, no_friends_yet):
        sleep = random.randrange(1, 5)
        lock.acquire()
        self.textfield.insert('end', '{} - нашел {} потенциальных друзей. Ждет {} секунд\n'.format(self.user[9],
                                                                                                    len(no_friends_yet),
                                                                                                    sleep))
        self.textfield.see('end')
        lock.release()
        time.sleep(sleep)
        self.not_added = 0
        count = 0
        while count < len(no_friends_yet):
            lock.acquire()
            profiles = get_profiles(session=self.user_friends[1], batch=no_friends_yet[count:count + 24])
            lock.release()
            count += 24
            # Обєднуємо масиви в один для зручності
            for i in profiles[1]:
                for z in profiles[0]:
                    if i['id'] == z[0]['id']:
                        z[0].update(i)
            # Запускаємо цикл для першої пачки людей
            for no_friendID in profiles[0]:

                # Перевіряємо чи не натиснута кнопка СТОП
                if WORK == False:
                    raise Exception('Stop')

                if self.not_added == 20: break  # Логіка безперспективного додавання

                # Перевіряємо чи нема не прочитаних повідомлень, якщо є, то відправляємо стандартне повідомлення.
                if self.auto_answer == 1:
                    lock.acquire()
                    self.autoAnswerOnMessage()
                    lock.release()

                # Перевіряємо чи не потрібно постити на стіну, якщо так, то виконуємо метод постингу.
                if self.auto_post == 1:
                    lock.acquire()
                    self.checkIfNeedCopy()
                    lock.release()

                # Перевіряємо чи не потрібно запрошувати в групу, якщо так, то виконуємо метод запрошення.
                if self.invite_to_group_id != 0:
                    lock.acquire()
                    self.inviteToGroup()
                    lock.release()

                # Перевіряємо чи не перебільшений ліміт на день
                lock.acquire()
                send_and_max_request = database.sendRequest(self.user[0])
                if send_and_max_request[1] == send_and_max_request[0]:
                    self.textfield.insert('end','{} - прекратил работу. Отправлено макс к-во запросов на день\n'.format(self.user[9]))
                    self.textfield.see('end')
                    raise Exception('Stop')
                lock.release()
                sleep = random.randrange(1, 5)
                user_name = no_friendID[0]['first_name'].encode('utf8') + ' ' + no_friendID[0]['last_name'].encode('utf8')
                lock.acquire()
                self.textfield.insert('end', '{} - открыл профиль не друга {}. Ждет {} секунд\n'.format(self.user[9],
                                                                                                         user_name,
                                                                                                         sleep))
                self.textfield.see('end')
                lock.release()
                time.sleep(sleep)

                # Якщо сторінка друга видалена то vk вертає error. Тут його ловимо і виводимо
                try:
                    # Перевіряємо чи користувач активний (тобто заходив у ВК протягом останніх 2х тижнів)
                    if time.time() - no_friendID[0]['last_seen']['time'] > 1210000:
                        raise Exception('Пользователь не заходил > 2 недель')

                    if 'counters' not in no_friendID[0]:
                        raise Exception('Пользователь ограничел доступ к странице')

                    # Перевіряємо чи у користувача не більше друзів ніж дозволено у нас
                    if no_friendID[0]['counters']['friends'] >= self.max_friends:
                        raise Exception('У пользователя > {} друзей'.format(self.max_friends))

                    # Перевіряємо чи користувач потрібної нам статі
                    if no_friendID[0]['sex'] == self.friend_sex or self.friend_sex == 3:
                        pass
                    else:
                        raise Exception('Пол пользователь не подходит')

                    # Якщо спільних друзів більше ніж мінімально то йдемо далі.
                    if no_friendID[0]['counters']['mutual_friends'] >= self.min_mutal:
                        # Перевіряємо чи нема ботів-сторінок в друзях. Якщо є, то не додаємо їх.
                        if [i for i in no_friendID[0]['common_friends'] if i in bots_id] != []:
                            self.not_added += 1
                            raise Exception('найдено общего друга с ботом в списке')
                            # Додаємо в друзі або ловимо капчу (якщо буде завершуємо роботу цього бота)
                        try:
                            sleep = random.randrange(self.min, self.max)
                            lock.acquire()
                            add_to_friend(session=self.user_friends[1], id=no_friendID[0]['id'])
                            self.textfield.insert('end',
                                                  '{} - отправил запрос в друзья юзеру {}. Ждет {} секунд\n'.format(
                                                      self.user[9],
                                                      user_name,
                                                      sleep))
                            self.not_added = 0
                            database.sendRequestCount(self.user[0])  # Додаємо в каунтер +1
                            self.textfield.see('end')
                            database.addToStatistics(self.user[9].decode('utf8'), 'friend')  # Додаємо в статистику
                            lock.release()
                            time.sleep(sleep)

                        except Exception as e:
                            raise NameError('Нужно ввести капчу')
                    else:
                        sleep = random.randrange(1, 5)
                        lock.acquire()
                        self.textfield.insert('end',
                                              '{} - не нашел {} общих друзей с {}. Ждет {} секунд\n'.format(self.user[9],
                                                                                                             self.min_mutal,
                                                                                                             user_name,
                                                                                                             sleep))
                        self.textfield.see('end')
                        lock.release()
                        self.not_added += 1
                        time.sleep(sleep)
                except Exception as e:
                    if e.__class__ == NameError:
                        lock.acquire()
                        self.textfield.insert('end',
                                              '{} - прекратил работу, причина: {}\n'.format(self.user[9], e.message))
                        self.textfield.see('end')
                        lock.release()
                        raise Exception
                    lock.acquire()
                    self.textfield.insert('end', '{} - не додал в друзья, причина: {}\n'.format(self.user[9], e.message))
                    self.textfield.see('end')
                    lock.release()
                    self.not_added += 1

    # Метод к-сті запросів за день, а також максимальної к-сті
    def requestPerDay(self):
        database.maxRequestSend(self.user[0])
        day = datetime.strptime(self.user[7], '%Y-%m-%d').date()
        if day != date.today():
            database.updateUserRequest(self.user[0])

    # Метод автоматичної відповіді на повідомлення та коментарі до фото
    def autoAnswerOnMessage(self):
        new_messages = get_messages(self.user_friends[1])
        if new_messages['count'] != 0:
            for i in new_messages['items']:
                send_message(session=self.user_friends[1], f_id=i['message']['user_id'], message=self.message)
                database.addToStatistics(self.user[9].decode('utf8'), 'message')  # Додаємо в статистику

            sleep = random.randrange(self.min, self.max)
            self.textfield.insert('end', '{} - ответил на сообщение. Ждет {} секунд\n'.format(self.user[9], sleep))
            self.textfield.see('end')
            time.sleep(sleep)

        # Автоматична відповідь для коментарів під фото
        config = SafeConfigParser()
        config.read('config.ini')
        last_comment_data = config.getint('photo', 'auto_answer_on_comments')
        new_comments = get_comments_on_photo(self.user_friends[1], last_comment_data)
        if new_comments['count'] != 0:
            for i in new_comments['items']:
                if i['date'] >= last_comment_data:
                    send_message(session=self.user_friends[1], f_id=i['feedback']['from_id'], message=self.message)
                    database.addToStatistics(self.user[9].decode('utf8'), 'message')  # Додаємо в статистику
            config.set('photo', 'auto_answer_on_comments', str(int(time.time())))
            with open('config.ini', 'w') as f:
                config.write(f)

            sleep = random.randrange(self.min, self.max)
            self.textfield.insert('end', '{} - ответил на коментарий. Ждет {} секунд\n'.format(self.user[9], sleep))
            self.textfield.see('end')
            time.sleep(sleep)

    # Мотод для копіювання постів
    def checkIfNeedCopy(self):

        config = SafeConfigParser()
        config.read('config.ini')
        post_date = config.getint('post', 'date')
        main_is_group = config.getint('post', 'main_is_group')

        # Метод ділиться на дві частини спочатку дивимось,
        # якщо це головна сторінка або група є головною то виконуємо перший блок, якщо не головна то другий
        # ----- Логіка для головної сторінки -----:
        # В конфіг ми записали дату останнього посту, тут ми перевіряємо чи не зявився новий пост,
        # Якщо зявився то формуємо нові задачі (в базу) для інших сторінок ботів, щоб вони потім зробили пост.
        # ----- Логіка для інших сторінок ботів (user[10] == 0) -----:
        # Перевіряємо чи є у базі завдання на пост, якщо є то постимо.

        if self.user[10] == 1 or main_is_group != 0:
            if self.user[10] == 1:
                owner_id = self.user[6]
            else:
                owner_id = '-' + str(main_is_group)

            post = get_last_post(self.user_friends[1], owner_id)
            if post['items'][0]['date'] > post_date:

                attachments = ''
                for p in post['items'][0]['attachments']:
                    attachments = attachments + 'photo' + str(p['photo']['owner_id']) + '_' + str(
                        p['photo']['id']) + ','

                # Збарігаємо нове значення дати останнього посту в конфіг файл
                config.set('post', 'date', str(post['items'][0]['date']))
                with open('config.ini', 'w') as f:
                    config.write(f)

                # Створюємо завдання в базі даних для інших ботів щоб вони зробили пости
                con = db.connect(database="vkbot")
                cur = con.cursor()
                users = cur.execute("SELECT * FROM users WHERE start_work=1;").fetchall()
                for u in users:
                    if u[10] == 0:  # Щоб створити завдання всім крім основної сторінки
                        cur.execute("INSERT INTO tasks (bot_id, text, attachments) VALUES (?, ?, ?)",
                                    (u[0], post['items'][0]['text'], attachments))
                        con.commit()

        if self.user[10] == 0:
            con = db.connect(database="vkbot")
            cur = con.cursor()
            task_for_user = (cur.execute("SELECT * FROM tasks WHERE bot_id=?;", (self.user[0],))).fetchall()
            for task in task_for_user:
                post_on_wall(self.user_friends[1], task)
                # Видаляємо завдання після посту, щоб бот потім знову це не запостив
                cur.execute("DELETE FROM tasks WHERE id=?;", (task[0],))
                con.commit()
                database.addToStatistics(self.user[9].decode('utf8'), 'post')  # Додаємо в статистику

    # Мотод для заливки фото
    def uploadPhoto(self):
        # ----------Логіка--------------#
        # Беремо назву папки яку вибрав юзер, перевіряємо чи є такий альбом у сторінки
        # Якщо нема то створюємо новий альбом і заливаємо фото

        config = SafeConfigParser()
        config.read('config.ini')
        dir = config.get('photo', 'upload_dir')
        title = dir.rsplit('/')
        response = get_albums_title(login=self.user[1], password=self.user[2])
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
            new_album = create_new_album(session, title[-1])
            album_id = new_album['id']

        upload_photo_to_album(session, album_id, dir, self.textfield, self.user)

    def getSessionAndFriend(self):
        # Отримуємо всіх друзів юзера (тянемо тільки ID). Також ловимо помилку про авторизацію і виводимо її
        try:
            sleep = random.randrange(1, 5)
            user_friends = get_friends_and_session(login=self.user[1], password=self.user[2])
            # random.shuffle(user_friends[0]['items'])  # Перемішуємо друзів, щоб не проходитись завжди від початку списку
            self.textfield.insert('end',
                                  '{} - зашел к друзьям у него их {}. Ждет {} секунд\n'.format(self.user[9],
                                                                                                str(user_friends[0][
                                                                                                        'count']),
                                                                                                sleep))
            time.sleep(sleep)
            self.textfield.see('end')
            return user_friends
        except Exception as e:
            self.textfield.insert('end', '{} - прекратил работу, причина : {}\n'.format(self.user[9], e.message))
            self.textfield.see('end')

    def getSuggestedFriends(self):
        no_friends_yet = []
        suggested = get_suggestions(session=self.user_friends[1])
        for us in suggested['items']:
            if us['id'] in bots_id: continue
            if time.time() - us['last_seen']['time'] > 1210000: continue
            if us['sex'] == self.friend_sex or self.friend_sex == 3:
                pass
            else:
                continue
            no_friends_yet.append(us['id'])
        return no_friends_yet

    # Метод для запрошень в групу
    def inviteToGroup(self):
        session = self.user_friends[1]
        group_id = self.invite_to_group_id
        if self.for_invite == []:
            friends = self.user_friends[0]['items'][:500]
            self.for_invite = check_is_group_members(session, group_id, friends)
        for i in self.for_invite:
            if i['member'] == 0:
                if 'invitation' in i:
                    self.for_invite.remove(i)
                    continue
                try:
                    invite_to_group(session, group_id, i['user_id'])
                except Exception as e:
                    if e.code == 15:
                        time.sleep(1)
                        continue

                    if e.code == 14:
                        self.textfield.insert('end', '{} - прекратил работу, найдена капча\n'.format(self.user[9]))
                        self.textfield.see('end')
                        raise Exception('Stop')

                sleep = random.randrange(self.min, self.max)
                self.textfield.insert('end', '{} - пригласил друга в групу. Ждет {} секунд \n'.format(self.user[9],
                                                                                                      sleep))
                time.sleep(sleep)
                self.textfield.see('end')
                database.addToStatistics(self.user[9].decode('utf8'), 'invite')  # Додаємо в статистику
                self.for_invite.remove(i)
                break
            else:
                self.for_invite.remove(i)


# Цю зміннну потрібно щоб перевірити чи ботів сторінок нема у друзях.
bots_id = []


# Метод створює паралельні процеси. Для кожного юзера свій процес
def goWork(textfield):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    for i in cur.execute("SELECT * FROM users;"):
        bots_id.append(i[6])
        if i[5] == 1:
            t = threading.Thread(target=BotLogic(i, textfield).worker)
            t.start()

    textfield.insert('end', "Все потоки запущено, Faby начал работать!\n")
