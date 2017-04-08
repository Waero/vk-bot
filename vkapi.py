#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
import time
import vk
import database

APP_ID = 5677795


# Метод створює сесію і витягує друзів користувача
def get_friends_and_session(login, password):
    session = vk.AuthSession(scope='friends, messages, wall, photos, groups, notifications', app_id='5965576',
                             user_login=login, user_password=password)
    vkApi = vk.API(session, v='5.62')
    uf = vkApi.friends.get(order='hints')
    # uf - список всіх друзів
    # session - Сесія юзера
    return uf, session


# Метод витягує id користувача
def get_vk_id(login, password):
    session = vk.AuthSession(app_id='5965576', user_login=login, user_password=password)
    vkApi = vk.API(session, v='5.62')
    vk_id = vkApi.users.get()
    return vk_id


# Метод витягує профіль юзера по ID
def get_user(session, id):
    vkApi = vk.API(session, v='5.62')
    u = vkApi.users.get(user_ids=id, fields='last_seen, counters, sex, mutual_friends')
    return u


# Метод витягує друзів друга по ID, якщо сторінка заблокована то вертаємо 0
def get_friends(session, id):
    vkApi = vk.API(session, v='5.62')
    try:
        u = vkApi.friends.get(user_id=id, order='hints')
    except Exception as e:
        print e
        u = 0
    return u


# Метод витягує спільних друзів карент юзера і юзера (ID)
def get_mutual_friends(session, id):
    vkApi = vk.API(session, v='5.62')
    mutal_friends = vkApi.friends.getMutual(target_uid=id)
    return mutal_friends


# Метод відправляємо заявку в друзі (ID)
def add_to_friend(session, id):
    vkApi = vk.API(session, v='5.62')
    added_friend = vkApi.friends.add(user_id=id)
    return added_friend


def add_to_friend_captcha(session, id, captcha_sid, captcha_key):
    vkApi = vk.API(session, v='5.62')
    added_friend = vkApi.friends.add(user_id=id, captcha_sid=captcha_sid, captcha_key=captcha_key)
    return added_friend


# Метод витягує кому вже відправлялись заявки
def get_requests(session):
    vkApi = vk.API(session, v='5.62')
    sended_request = vkApi.friends.getRequests(out=1, count=1000)
    return sended_request


# Метод витягує нові повідомлення
def get_messages(session):
    vkApi = vk.API(session, v='5.62')
    new_messages = vkApi.messages.getDialogs(unread=1)
    return new_messages


# Метод відправки повідомлення для авто-ответа
def send_message(session, f_id, message):
    vkApi = vk.API(session, v='5.62')
    vkApi.messages.send(user_id=f_id, message=message)


# Отримуємо дату останнього посту на стіні
def get_last_post(session, owner_id):
    vkApi = vk.API(session, v='5.62')
    post = vkApi.wall.get(count=1, filter='owner', owner_id=owner_id)
    return post


# Постимо на стіні сторінки
def post_on_wall(session, task):
    vkApi = vk.API(session, v='5.62')
    post = vkApi.wall.post(message=task[2], attachments=task[3])
    return post


# Метод для витягнення дати останнього посту коли вибираємо головну сторінку
def get_last_post_date(login, password):
    session = vk.AuthSession(app_id='5677795', user_login=login, user_password=password)
    vkApi = vk.API(session, v='5.62')
    date = vkApi.wall.get(count=1, filter='owner')
    return date['items'][0]['date']


# Метод для витягнення дати останнього посту з групи коли вона головна сторінка
def get_last_post_date_group(owner_id):
    session = vk.AuthSession()
    vkApi = vk.API(session, v='5.62')
    date = vkApi.wall.get(owner_id=owner_id, count=1, filter='owner')
    return date['items'][0]['date']


# Метод щоб отримати id групи
def get_group_id(group_ids):
    session = vk.AuthSession()
    vkApi = vk.API(session, v='5.62')
    response = vkApi.groups.getById(group_ids=group_ids)
    return response[0]['id']


# Метод витягуємо назви всіх альбомів
def get_albums_title(login, password):
    session = vk.AuthSession(scope='photos', app_id='5677795', user_login=login, user_password=password)
    vkApi = vk.API(session, v='5.62')
    albums = vkApi.photos.getAlbums()
    return session, albums


# Метод створювати новий альбом
def create_new_album(session, title):
    vkApi = vk.API(session, v='5.62')
    album = vkApi.photos.createAlbum(title=title)
    return album


# Метод загрузки фото
def upload_photo_to_album(session, album_id, directory, textfield, user):
    vkApi = vk.API(session, v='5.62')
    directory = directory.decode('utf-8')
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if 'Thumbs.db' in files: files.remove('Thumbs.db')  # Тимчасове рішення, треба зробити перевірку щоб додавати в масив тільки фото
    textfield.insert('end', '{} - готовит загрузку {} фото\n'.format(user[9], len(files)))
    textfield.see('end')

    for f in files:
        upload_url = vkApi.photos.getUploadServer(album_id=album_id)
        fil = os.path.join(directory, f)
        fil = os.path.normpath(fil)
        r = requests.post(upload_url['upload_url'], files={'photo': open(fil, "rb")})
        params = {'server': r.json()['server'], 'photos_list': r.json()['photos_list'], 'hash': r.json()['hash'], 'album_id': album_id}
        vkApi.photos.save(**params)
        time.sleep(1)
        textfield.insert('end', '{} - загрузил новое фото\n'.format(user[9]))
        textfield.see('end')
        database.addToStatistics(user[9].decode('utf8'), 'photo')  # Додаємо в статистику


def get_suggestions(session):
    vkApi = vk.API(session, v='5.62')
    suggested = vkApi.friends.getSuggestions(filter='mutual', fields='last_seen, sex')
    return suggested


# Додавання в групу
def invite_to_group(session, group_id, user_id):
    vkApi = vk.API(session, v='5.62')
    invite = vkApi.groups.invite(group_id=group_id, user_id=user_id)
    return invite


def check_is_group_members(session, group_id, user_ids):
    vkApi = vk.API(session, v='5.62')
    members = vkApi.groups.isMember(group_id=group_id, user_ids=user_ids, extended=1)
    return members


# Витягуємо коменти до фото через нотіфікейшини
def get_comments_on_photo(session, start_time):
    vkApi = vk.API(session, v='5.62')
    comments = vkApi.notifications.get(filters='comments', start_time=start_time)
    return comments


def get_candidate(session, bot_friend, max_friends):
    vkApi = vk.API(session, v='5.62')
    data = vkApi.execute.getCandidate(a=bot_friend[0], b=bot_friend[1], c=bot_friend[2],
                                      d=bot_friend[3], e=bot_friend[4], max=max_friends)
    return data


def get_profiles(session, batch):
    vkApi = vk.API(session, v='5.62')
    data = vkApi.execute.getProfiles(a=batch)
    return data


def accept_friend(session):
    vkApi = vk.API(session, v='5.63')
    data = vkApi.execute(code='var a = API.friends.getRequests().items; var count = 0; while (a.length > count)'
                              ' { API.friends.add({"user_id": a[count]});} return a;')
    return data