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
lock2 = threading.Lock()
db_lock = threading.Lock()
urllib3.disable_warnings()


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
        self.min_mutual = config.getint('main', 'mutal')
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
        # Перевірка максимальних і відправлених реквестів
        self.request_per_day()
        # При старті присвоюємо юзерам час очікування, щоб кожен стартанув у різний час
        sleep = random.randrange(self.min, self.max)
        self.wr_in_progress('настроен и ждет', sleep)
        time.sleep(sleep)

        if self.upload_photo == 1:
            self.upload_photo_in_album()

        while WORK:
                self.user_friends = self.find_session_and_friend()
                with lock:
                    accept_friend(self.user_friends[1])
                # Перевіряємо чи не вимкнуто роботу бота
                if not WORK:
                    raise Exception('Stop')

                # Перевіряємо чи будемо додавати в друзі
                if self.add_to_friend == 1:
                    self.invite_to_friend()

                # Перевіряємо чи нема не прочитаних повідомлень, якщо є, то відправляємо стандартне повідомлення.
                if self.auto_answer == 1:
                    sleep = random.randrange(self.min, self.max)
                    self.wr_in_progress('проверяет сообщения', sleep)
                    time.sleep(sleep)
                    self.answer_on_message()
                # Перевіряємо чи не потрібно постити на стіну, якщо так, то виконуємо метод постингу.
                if self.auto_post == 1:
                    sleep = random.randrange(self.min, self.max)
                    self.wr_in_progress('проверяет стену на постинг', sleep)
                    time.sleep(sleep)
                    self.check_if_need_copy_post()

                    # Перевіряємо чи не потрібно запрошувати в групу, якщо так, то виконуємо метод запрошення.
                if self.invite_to_group_id != 0:
                    sleep = random.randrange(self.min, self.max)
                    self.wr_in_progress('готовит приглашение в групу', sleep)
                    time.sleep(sleep)
                    self.invite_to_group()

    def invite_to_friend(self):
        # ------------Дивимось по якому принципу будемо додавати друзів  -------------#
        if self.suggested_type == 1:
            no_friends_yet = self.find_suggested_friends()
            self.add_no_friends_yet(no_friends_yet)
        else:
            bot_friend = set(self.user_friends[0]['items']) - set(bots_id)
            bot_friend = list(bot_friend)
            counts = 0
            while len(bot_friend) > counts:
                b_counts = len(bot_friend) if len(bot_friend) < counts + 5 else counts + 5
                with lock:
                    data = get_candidate(session=self.user_friends[1], bot_friend=bot_friend[counts:b_counts], max_friends=self.max_friends)
                counts += (bot_friend.index(data[3][0]['id']) + 1)
                sleep = random.randrange(1, 6)
                friend_profile = data[3]
                friend_name = friend_profile[0]['first_name'].encode('utf8') + ' ' + friend_profile[0]['last_name'].encode('utf8')
                self.wr_in_progress('зашел к друзьям друга {}'.format(friend_name), sleep)
                time.sleep(sleep)

                # Знаходимо людей яких у нас ще нема в друзях і відсіюємо тих кому вже відправляли запит, і тих хто у нас у спільних
                profiles = data[0]
                mutual_friends = data[1]
                sended_request = data[2]
                no_friends_yet = []
                for i in profiles:
                    if i['id'] not in mutual_friends:
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

                self.add_no_friends_yet(candidates_in_friends)

    # Метод додавання друзів
    def add_no_friends_yet(self, no_friends_yet):
        sleep = random.randrange(1, 6)
        self.wr_in_progress('нашел {} потенциальных друзей'.format(len(no_friends_yet)), sleep)
        time.sleep(sleep)
        self.not_added = 0
        count = 0
        while count < len(no_friends_yet):
            b_count = len(no_friends_yet) if count + 24 > len(no_friends_yet) else count + 24
            with lock:
                profiles = get_profiles(session=self.user_friends[1], batch=no_friends_yet[count:b_count])
            count += 24
            # Обєднуємо масиви в один для зручності
            for i in profiles[1]:
                for z in profiles[0]:
                    if i['id'] == z[0]['id']:
                        z[0].update(i)
            # Запускаємо цикл для першої пачки людей
            for no_friendID in profiles[0]:
                # Видаляємо тих у кого більше друзів ніж у нас дозволено
                if 'counters' in no_friendID[0]:
                    if no_friendID[0]['counters']['friends'] >= self.max_friends:
                        continue
                    if no_friendID[0]['counters']['mutual_friends'] <= self.min_mutual:
                        continue
                # Перевіряємо чи не натиснута кнопка СТОП
                if not WORK:
                    raise Exception('Stop')

                if self.not_added == 20: break  # Логіка безперспективного додавання

                # Перевіряємо чи нема не прочитаних повідомлень, якщо є, то відправляємо стандартне повідомлення.
                if self.auto_answer == 1:
                    self.answer_on_message()

                # Перевіряємо чи не потрібно постити на стіну, якщо так, то виконуємо метод постингу.
                if self.auto_post == 1:
                    self.check_if_need_copy_post()

                # Перевіряємо чи не потрібно запрошувати в групу, якщо так, то виконуємо метод запрошення.
                if self.invite_to_group_id != 0:
                    self.invite_to_group()

                # Перевіряємо чи не перебільшений ліміт на день
                with db_lock:
                    send_and_max_request = database.sendRequest(self.user[0])
                if send_and_max_request[1] == send_and_max_request[0]:
                    self.wr_in_progress('прекратил работу. Отправлено макс к-во запросов на день', 0)
                    raise Exception('Stop')

                sleep = random.randrange(1, 7)
                user_name = no_friendID[0]['first_name'].encode('utf8') + ' ' + no_friendID[0]['last_name'].encode('utf8')
                self.wr_in_progress('открыл профиль не друга {}'.format(user_name), sleep)
                time.sleep(sleep)

                # Якщо сторінка друга видалена то vk вертає error. Тут його ловимо і виводимо
                try:
                    sleep = random.randrange(1, 6)
                    if 'counters' not in no_friendID[0]:
                        self.wr_in_progress('не додал в друзья, причина: Пользователь ограничел доступ к странице', sleep)
                        self.not_added += 1
                        time.sleep(sleep)
                        continue

                    # Перевіряємо чи у користувача не більше друзів ніж дозволено у нас (треба видалити цю перевірку)
                    if no_friendID[0]['counters']['friends'] >= self.max_friends:
                        self.wr_in_progress('не додал в друзья, причина: У пользователя > {} друзей'.format(self.max_friends), sleep)
                        self.not_added += 1
                        time.sleep(sleep)
                        continue

                    # Якщо спільних друзів більше ніж мінімально то йдемо далі.
                    if no_friendID[0]['counters']['mutual_friends'] >= self.min_mutual:
                        # Перевіряємо чи нема ботів-сторінок в друзях. Якщо є, то не додаємо їх.
                        if [i for i in no_friendID[0]['common_friends'] if i in bots_id] != []:
                            self.wr_in_progress('не додал в друзья, причина: найдено общего друга с ботом в списке', sleep)
                            self.not_added += 1
                            time.sleep(sleep)
                            continue

                            # Додаємо в друзі або ловимо капчу (якщо буде завершуємо роботу цього бота)
                        try:
                            sleep = random.randrange(self.min, self.max)
                            with lock:
                                add_to_friend(session=self.user_friends[1], id=no_friendID[0]['id'])
                            self.not_added = 0
                            with db_lock:
                                database.sendRequestCount(self.user[0])  # Додаємо в каунтер +1
                                database.addToStatistics(self.user[9].decode('utf8'), 'friend')  # Додаємо в статистику
                            self.wr_in_progress('отправил запрос в друзья -> {}'.format(user_name), sleep)
                            time.sleep(sleep)

                        except Exception as e:
                            if e.code == 1:
                                raise NameError('макс к-во заявок на день')
                            raise NameError('Нужно ввести капчу')
                    else:
                        sleep = random.randrange(1, 6)
                        self.wr_in_progress('не нашел {} общих друзей с {}'.format(self.min_mutual, user_name), sleep)
                        self.not_added += 1
                        time.sleep(sleep)
                except Exception as e:
                    if e.__class__ == NameError:
                        self.wr_in_progress('прекратил работу, причина: {}'.format(e.message), 0)
                        raise Exception
                    self.wr_in_progress('не додал в друзья, причина: {}'.format(e.message), 0)
                    self.not_added += 1

    # Метод к-сті запросів за день, а також максимальної к-сті
    def request_per_day(self):
        with db_lock:
            database.maxRequestSend(self.user[0])
            day = datetime.strptime(self.user[7], '%Y-%m-%d').date()
            if day != date.today():
                database.updateUserRequest(self.user[0])

    # Метод автоматичної відповіді на повідомлення та коментарі до фото
    def answer_on_message(self):
        with lock:
            new_messages = get_messages(self.user_friends[1])
        if new_messages['count'] != 0:
            for i in new_messages['items']:
                with lock:
                    send_message(session=self.user_friends[1], f_id=i['message']['user_id'], message=self.message)
                with db_lock:
                    database.addToStatistics(self.user[9].decode('utf8'), 'message')  # Додаємо в статистику

            sleep = random.randrange(self.min, self.max)
            self.wr_in_progress('ответил на сообщение', sleep)
            time.sleep(sleep)

        # Автоматична відповідь для коментарів під фото
        config = SafeConfigParser()
        config.read('config.ini')
        last_comment_data = config.getint('photo', 'auto_answer_on_comments')
        with lock:
            new_comments = get_comments_on_photo(self.user_friends[1], last_comment_data)
        if new_comments['count'] != 0:
            for i in new_comments['items']:
                if i['date'] >= last_comment_data:
                    with lock:
                        send_message(session=self.user_friends[1], f_id=i['feedback']['from_id'], message=self.message)
                    with db_lock:
                        database.addToStatistics(self.user[9].decode('utf8'), 'message')  # Додаємо в статистику
            config.set('photo', 'auto_answer_on_comments', str(int(time.time())))
            with open('config.ini', 'w') as f:
                config.write(f)

            sleep = random.randrange(self.min, self.max)
            self.wr_in_progress('ответил на коментарий', sleep)
            time.sleep(sleep)

    # Мотод для копіювання постів
    def check_if_need_copy_post(self):
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
            with lock:
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
                with db_lock:
                    con = db.connect(database="vkbot")
                    cur = con.cursor()
                    users = cur.execute("SELECT * FROM users WHERE start_work=1;").fetchall()
                    for u in users:
                        if u[10] == 0:  # Щоб створити завдання всім крім основної сторінки
                            cur.execute("INSERT INTO tasks (bot_id, text, attachments) VALUES (?, ?, ?)",
                                        (u[0], post['items'][0]['text'], attachments))
                            con.commit()

        if self.user[10] == 0:
            with db_lock:
                con = db.connect(database="vkbot")
                cur = con.cursor()
                task_for_user = (cur.execute("SELECT * FROM tasks WHERE bot_id=?;", (self.user[0],))).fetchall()
                for task in task_for_user:
                    with lock:
                        post_on_wall(self.user_friends[1], task)
                    # Видаляємо завдання після посту, щоб бот потім знову це не запостив
                    cur.execute("DELETE FROM tasks WHERE id=?;", (task[0],))
                    con.commit()
                    database.addToStatistics(self.user[9].decode('utf8'), 'post')  # Додаємо в статистику

    # Мотод для заливки фото
    def upload_photo_in_album(self):
        # ----------Логіка--------------#
        # Беремо назву папки яку вибрав юзер, перевіряємо чи є такий альбом у сторінки
        # Якщо нема то створюємо новий альбом і заливаємо фото

        config = SafeConfigParser()
        config.read('config.ini')
        directory = config.get('photo', 'upload_dir')
        title = directory.rsplit('/')
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
            with lock:
                new_album = create_new_album(session, title[-1])
                album_id = new_album['id']

        upload_photo_to_album(session, album_id, directory, self.textfield, self.user)

    def find_session_and_friend(self):
        # Отримуємо всіх друзів юзера (тянемо тільки ID). Також ловимо помилку про авторизацію і виводимо її
        try:
            sleep = random.randrange(1, 6)
            with lock:
                user_friends = get_friends_and_session(login=self.user[1], password=self.user[2])
                time.sleep(0.5)
            random.shuffle(user_friends[0]['items'])  # Перемішуємо друзів, щоб не проходитись завжди від початку списку
            self.wr_in_progress('зашел к друзьям у него их {}'.format(str(user_friends[0]['count'])), sleep)
            time.sleep(sleep)
            return user_friends

        except Exception as e:
            if 'Invalid URL' in e.message:
                self.wr_in_progress('прекратил работу, причина : Проверте страницу', 0)
            else:
                self.wr_in_progress('прекратил работу, причина : {}'.format(e.message), 0)
            raise Exception('Stop')

    def find_suggested_friends(self):
        no_friends_yet = []
        with lock:
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
    def invite_to_group(self):
        session = self.user_friends[1]
        group_id = self.invite_to_group_id
        if self.for_invite == []:
            friends = self.user_friends[0]['items'][:500]
            with lock:
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
                        self.wr_in_progress('прекратил работу, найдена капча',0)
                        raise Exception('Stop')

                sleep = random.randrange(self.min, self.max)
                self.wr_in_progress('пригласил друга в групу', sleep)
                time.sleep(sleep)
                with db_lock:
                    database.addToStatistics(self.user[9].decode('utf8'), 'invite')  # Додаємо в статистику
                self.for_invite.remove(i)
                break
            else:
                self.for_invite.remove(i)

    def wr_in_progress(self, text, sleep):
        with lock2:
            if sleep == 0:
                self.textfield.insert('end', '{} - {}.\n'.format(self.user[9], text))
                self.textfield.see('end')
            else:
                self.textfield.insert('end', '{} - {}. Ждет {} секунд\n'.format(self.user[9], text, sleep))
                self.textfield.see('end')


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
