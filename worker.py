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
        self.requestPerDay()
        # При старті присвоюємо юзерам час очікування, щоб кожен стартанув у різний час
        sleep = random.randrange(self.min, self.max)
        self.textfield.insert('end', "{} - настроен и ждет {} секунд \n".format(self.user[9], sleep))
        time.sleep(sleep)

        if self.upload_photo == 1:
            self.uploadPhoto()

        while WORK == True:

            self.user_friends = self.getSessionAndFriend()

            file = open('myFriend.txt', 'w')
            for item in self.user_friends[0]['items']:
                file.write(str(item) + '\n')
            file.close()

            with open('sendRequest.txt', 'w') as f:
                f.write('\n')
            f.close()

            # Перевіряємо чи не вимкнуто роботу бота
            if WORK == False:
                raise Exception('Stop')

            # Перевіряємо чи будемо додавати в друзі
            if self.add_to_friend == 1:
                self.inviteToFriend()

            # Перевіряємо чи нема не прочитаних повідомлень, якщо є, то відправляємо стандартне повідомлення.
            if self.auto_answer == 1:
                sleep = random.randrange(self.min, self.max)
                self.textfield.insert('end', '{} - проверяет сообщения. Ждет {} секунд \n'.format(self.user[9], sleep))
                self.textfield.see('end')
                time.sleep(sleep)
                self.autoAnswerOnMessage()
            # Перевіряємо чи не потрібно постити на стіну, якщо так, то виконуємо метод постингу.
            if self.auto_post == 1:
                sleep = random.randrange(self.min, self.max)
                self.textfield.insert('end',
                                      '{} - проверяет стену на постинг. Ждет {} секунд \n'.format(self.user[9], sleep))
                self.textfield.see('end')
                time.sleep(sleep)
                self.checkIfNeedCopy()

                # Перевіряємо чи не потрібно запрошувати в групу, якщо так, то виконуємо метод запрошення.
            if self.invite_to_group_id != 0:
                sleep = random.randrange(self.min, self.max)
                self.textfield.insert('end',
                                      '{} - готовит приглашение в групу. Ждет {} секунд \n'.format(self.user[9], sleep))
                self.textfield.see('end')
                time.sleep(sleep)
                self.inviteToGroup()

    def inviteToFriend(self):
        # ------------Дивимось по якому принципу будемо додавати друзів  -------------#
        if self.suggested_type == 1:
            no_friends_yet = self.getSuggestedFriends()
            self.addNoFriendsYet(no_friends_yet)
        else:
            # Проходимось по всіх друзях юзера і по його друзях. Основний код
            for uid in self.user_friends[0]['items']:
                if uid in bots_id: continue  # Щоб не відкрити профіль бота!

                sleep = random.randrange(1, 5)

                # Витягуємо друзів друга, якщо сторінка заблоковано то вертаємо 0 і йдемо до наступного
                friends_from_friend = getFriends(session=self.user_friends[1], id=uid)
                if friends_from_friend == 0: continue

                friend_profile = getUser(session=self.user_friends[1], id=uid)
                if friend_profile[0]['counters'][
                    'friends'] >= self.max_friends: continue  # Йдемо до наступного друга, якщо у цього більше друзів ніж нам треба

                friend_name = friend_profile[0]['first_name'].encode('utf8') + ' ' + friend_profile[0][
                    'last_name'].encode('utf8')
                self.textfield.insert('end', '{} - зашел к друзьям друга {}. Ждет {} секунд \n'.format(self.user[9],
                                                                                                       friend_name,
                                                                                                       sleep))
                self.textfield.see('end')
                time.sleep(sleep)

                # Знаходимо людей яких у нас ще нема в друзях і віднімаємо тих кому вже відправляли запит
                mutal_friends = getMutalFriends(session=self.user_friends[1], id=uid)
                sended_request = getRequests(session=self.user_friends[1])
                friends_without_mutal = set(friends_from_friend['items']) - set(mutal_friends)
                no_friends_yet = friends_without_mutal - set(sended_request['items'])
                no_friends_yet = getUser(session=self.user_friends[1], id=no_friends_yet)
                candidates_in_friends = []
                # Тимчасово для тесту пропуску заявок
                file = open('myFriend.txt', 'a')
                for item in sended_request['items']:
                    file.write(str(item) + '\n')
                file.close()
                # Відсіюємо тих хто нам не підходить по профайлу
                for t in no_friends_yet:
                    if 'deactivated' in t: continue
                    if time.time() - t['last_seen']['time'] > 1210000: continue

                    # Перевіряємо чи користувач потрібної нам статі
                    if t['sex'] == self.friend_sex or self.friend_sex == 3:
                        pass
                    else:
                        continue
                    if t['id'] == self.user[6]: continue  # щоб сам себе не додавав (про всяк випадок)
                    candidates_in_friends.append(t['id'])

                self.addNoFriendsYet(candidates_in_friends)

    # Метод додавання друзів(Потрібно буде розділити)
    def addNoFriendsYet(self, no_friends_yet):
        sleep = random.randrange(1, 5)
        self.textfield.insert('end', '{} - нашел {} потенциальных друзей. Ждет {} секунд \n'.format(self.user[9],
                                                                                                    len(no_friends_yet),
                                                                                                    sleep))
        self.textfield.see('end')
        time.sleep(sleep)
        self.not_added = 0

        # Відкриваємо профіль юзера з людей яких у нас ще нема в друзях
        for no_friendID in no_friends_yet:

            # Перевіряємо чи не натиснута кнопка СТОП
            if WORK == False:
                raise Exception('Stop')

            if self.not_added == 20: break  # Логіка безперспективного додавання

            # Перевіряємо чи нема не прочитаних повідомлень, якщо є, то відправляємо стандартне повідомлення.
            if self.auto_answer == 1:
                self.autoAnswerOnMessage()

            # Перевіряємо чи не потрібно постити на стіну, якщо так, то виконуємо метод постингу.
            if self.auto_post == 1:
                self.checkIfNeedCopy()

            # Перевіряємо чи не потрібно запрошувати в групу, якщо так, то виконуємо метод запрошення.
            if self.invite_to_group_id != 0:
                self.inviteToGroup()

            # Перевіряємо чи не перебільшений ліміт на день
            send_and_max_request = database.sendRequest(self.user[0])
            if send_and_max_request[1] == send_and_max_request[0]:
                self.textfield.insert('end',
                                      '{} - прекратил работу. Отправлено макс к-во запросов на день \n'.format(
                                          self.user[9]))
                self.textfield.see('end')
                raise Exception('Stop')

            # Відкриваємо профіль користувача
            sleep = random.randrange(1, 5)
            open_user_profile = getUser(session=self.user_friends[1], id=no_friendID)
            user_name = open_user_profile[0]['first_name'].encode('utf8') + ' ' + open_user_profile[0][
                'last_name'].encode('utf8')
            self.textfield.insert('end', '{} - открыл профиль не друга {}. Ждет {} секунд \n'.format(self.user[9],
                                                                                                     user_name,
                                                                                                     sleep))
            self.textfield.see('end')
            time.sleep(sleep)

            # Якщо сторінка друга видалена то vk вертає error. Тут його ловимо і виводимо
            try:
                # Перевіряємо чи користувач активний (тобто заходив у ВК протягом останніх 2х тижнів)
                if time.time() - open_user_profile[0]['last_seen']['time'] > 1210000:
                    raise Exception('Пользователь не заходил > 2 недель')

                if 'counters' not in open_user_profile[0]:
                    raise Exception('Пользователь ограничел доступ к странице')
                # Перевіряємо чи у користувача не більше друзів ніж дозволено у нас
                if open_user_profile[0]['counters']['friends'] >= self.max_friends:
                    raise Exception('У пользователя > {} друзей'.format(self.max_friends))

                # Перевіряємо чи користувач потрібної нам статі
                if open_user_profile[0]['sex'] == self.friend_sex or self.friend_sex == 3:
                    pass
                else:
                    raise Exception('Пол пользователь не подходит')

                # Перевіряємо чи є у нас більше мінімальної к-сті (min_mutal) спільних юзерів, якщо є, то додаємо в друзі, якщо ні, то відкриваємо наступного
                mutal = getMutalFriends(session=self.user_friends[1], id=no_friendID)

                # Якщо спільних друзів більше ніж мінімально то йдемо далі.
                if mutal.__len__() >= self.min_mutal:
                    # Перевіряємо чи нема ботів-сторінок в друзях. Якщо є, то не додаємо їх.
                    if [i for i in mutal if i in bots_id] != []:
                        self.not_added += 1
                        raise Exception('найдено общего друга с ботом в списке')
                        # Додаємо в друзі або ловимо капчу (якщо буде завершуємо роботу цього бота)
                    try:
                        sleep = random.randrange(self.min, self.max)
                        addToFriend(session=self.user_friends[1], id=no_friendID)
                        self.textfield.insert('end',
                                              '{} - отправил запрос в друзья юзеру {}. Ждет {} секунд \n'.format(
                                                  self.user[9],
                                                  user_name,
                                                  sleep))
                        self.not_added = 0
                        database.sendRequestCount(self.user[0])  # Додаємо в каунтер +1
                        self.textfield.see('end')
                        database.addToStatistics(self.user[9].decode('utf8'), 'friend')  # Додаємо в статистику

                        file = open('sendRequest.txt', 'a')
                        file.write(str(no_friendID) + '\n')
                        file.close()

                        time.sleep(sleep)

                    except Exception as e:
                        raise NameError('Нужно ввести капчу')
                else:
                    sleep = random.randrange(1, 5)
                    self.textfield.insert('end',
                                          '{} - не нашел {} общих друзей с {}. Ждет {} секунд \n'.format(self.user[9],
                                                                                                         self.min_mutal,
                                                                                                         user_name,
                                                                                                         sleep))
                    self.textfield.see('end')
                    self.not_added += 1
                    time.sleep(sleep)
            except Exception as e:
                if e.__class__ == NameError:
                    self.textfield.insert('end',
                                          '{} - прекратил работу, причина: {} \n'.format(self.user[9], e.message))
                    self.textfield.see('end')
                    raise Exception
                self.textfield.insert('end', '{} - не додал в друзья, причина: {} \n'.format(self.user[9], e.message))
                self.textfield.see('end')
                self.not_added += 1

    # Метод к-сті запросів за день, а також максимальної к-сті
    def requestPerDay(self):
        database.maxRequestSend(self.user[0])
        day = datetime.strptime(self.user[7], '%Y-%m-%d').date()
        if day != date.today():
            database.updateUserRequest(self.user[0])

    # Метод автоматичної відповіді на повідомлення та коментарі до фото
    def autoAnswerOnMessage(self):
        new_messages = getMessages(self.user_friends[1])
        if new_messages['count'] != 0:
            for i in new_messages['items']:
                sendMessage(session=self.user_friends[1], f_id=i['message']['user_id'], message=self.message)
                database.addToStatistics(self.user[9].decode('utf8'), 'message')  # Додаємо в статистику

            sleep = random.randrange(self.min, self.max)
            self.textfield.insert('end', '{} - ответил на сообщение. Ждет {} секунд \n'.format(self.user[9], sleep))
            self.textfield.see('end')
            time.sleep(sleep)

        # Автоматична відповідь для коментарів під фото
        config = SafeConfigParser()
        config.read('config.ini')
        last_comment_data = config.getint('photo', 'auto_answer_on_comments')
        new_comments = getCommentsOnPhoto(self.user_friends[1], last_comment_data)
        if new_comments['count'] != 0:
            for i in new_comments['items']:
                if i['date'] >= last_comment_data:
                    sendMessage(session=self.user_friends[1], f_id=i['feedback']['from_id'], message=self.message)
                    database.addToStatistics(self.user[9].decode('utf8'), 'message')  # Додаємо в статистику
            config.set('photo', 'auto_answer_on_comments', str(int(time.time())))
            with open('config.ini', 'w') as f:
                config.write(f)

            sleep = random.randrange(self.min, self.max)
            self.textfield.insert('end', '{} - ответил на коментарий. Ждет {} секунд \n'.format(self.user[9], sleep))
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

            post = getLastPost(self.user_friends[1], owner_id)
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
                postOnWall(self.user_friends[1], task)
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
        response = getAlbumsTitle(login=self.user[1], password=self.user[2])
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

        uploadPhotoToAlbum(session, album_id, dir, self.textfield, self.user)

    def getSessionAndFriend(self):
        # Отримуємо всіх друзів юзера (тянемо тільки ID). Також ловимо помилку про авторизацію і виводимо її
        try:
            sleep = random.randrange(1, 5)
            user_friends = getFriendsAndSession(login=self.user[1], password=self.user[2])
            # random.shuffle(user_friends[0]['items'])  # Перемішуємо друзів, щоб не проходитись завжди від початку списку
            self.textfield.insert('end',
                                  '{} - зашел к друзьям у него их {}. Ждет {} секунд \n'.format(self.user[9],
                                                                                                str(user_friends[0][
                                                                                                        'count']),
                                                                                                sleep))
            time.sleep(sleep)
            self.textfield.see('end')
            return user_friends
        except Exception as e:
            self.textfield.insert('end', '{} - прекратил работу, причина : {} \n'.format(self.user[9], e.message))
            self.textfield.see('end')

    def getSuggestedFriends(self):
        no_friends_yet = []
        suggested = getSuggestions(session=self.user_friends[1])
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
            self.for_invite = checkIsGroupMembers(session, group_id, friends)
        for i in self.for_invite:
            if i['member'] == 0:
                if 'invitation' in i:
                    self.for_invite.remove(i)
                    continue
                try:
                    inviteToGroup(session, group_id, i['user_id'])
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
