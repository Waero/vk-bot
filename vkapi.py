#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import requests
import time
import vk
import database


# Метод створює сесію і витягує друзів користувача
def getFriendsAndSession(login, password):
    session = vk.AuthSession(scope='friends, messages, wall, photos', app_id='5677795', user_login=login, user_password=password)
    vkApi = vk.API(session, v='5.62')
    uf = vkApi.friends.get(order='hints')
    # uf - cписок всіх друзів
    # session - Сесія юзера
    return uf, session


# Метод витягує id користувача
def getVkId(login, password):
    session = vk.AuthSession(app_id='5677795', user_login=login, user_password=password)
    vkApi = vk.API(session, v='5.62')
    vk_id = vkApi.users.get()
    return vk_id


# Метод витягує профіль юзера по ID
def getUser(session,id):
    vkApi = vk.API(session, v='5.62')
    u = vkApi.users.get(user_ids=id, fields='last_seen, counters, sex')
    return u


# Метод витягує друзів друга по ID, якщо сторінка заблокована то вертаємо 0
def getFriends(session, id):
    vkApi = vk.API(session, v='5.62')
    try:
        u = vkApi.friends.get(user_id=id, order='hints')
    except Exception as e:
        print e
        u = 0
    return u


# Метод витягує спільних друзів карент юзера і юзера (ID)
def getMutalFriends(session, id):
    vkApi = vk.API(session, v='5.62')
    mutal_friends = vkApi.friends.getMutual(target_uid=id)
    return mutal_friends


# Метод відправляємо заявку в друзі (ID)
def addToFriend(session, id):
    vkApi = vk.API(session, v='5.62')
    added_friend = vkApi.friends.add(user_id=id)
    return added_friend


def addToFriendCaptcha(session, id, captcha_sid, captcha_key):
    vkApi = vk.API(session, v='5.62')
    added_friend = vkApi.friends.add(user_id=id, captcha_sid=captcha_sid, captcha_key=captcha_key)
    return added_friend


# Метод витягує кому вже відправлялись заявки
def getRequests(session):
    vkApi = vk.API(session, v='5.62')
    sended_request = vkApi.friends.getRequests(out=1)
    return sended_request


# Метод витягує нові повідомлення
def getMessages(session):
    vkApi = vk.API(session, v='5.62')
    new_messages = vkApi.messages.getDialogs(unread=1)
    return new_messages


# Метод відправки повідомлення для авто-ответа
def sendMessage(session, f_id, message):
    vkApi = vk.API(session, v='5.62')
    vkApi.messages.send(user_id=f_id, message=message)


# Отримуємо дату останнього посту на стіні
def getLastPost(session, owner_id):
    vkApi = vk.API(session, v='5.62')
    post = vkApi.wall.get(count=1, filter='owner', owner_id=owner_id)
    return post


# Постимо на стіні сторінки
def postOnWall(session, task):
    vkApi = vk.API(session, v='5.62')
    post = vkApi.wall.post(message=task[2], attachments=task[3])
    return post


# Метод для витягнення дати останнього посту коли вибираємо головну сторінку
def getLastPostDate(login, password):
    session = vk.AuthSession(app_id='5677795', user_login=login, user_password=password)
    vkApi = vk.API(session, v='5.62')
    date = vkApi.wall.get(count=1, filter='owner')
    return date['items'][0]['date']


# Метод для витягнення дати останнього посту з групи коли вона головна сторінка
def getLastPostDateGroup(owner_id):
    session = vk.AuthSession()
    vkApi = vk.API(session, v='5.62')
    date = vkApi.wall.get(owner_id=owner_id, count=1, filter='owner')
    return date['items'][0]['date']


# Метод щоб отримати id групи
def getGroupId(group_ids):
    session = vk.AuthSession()
    vkApi = vk.API(session, v='5.62')
    response = vkApi.groups.getById(group_ids=group_ids)
    return response[0]['id']


# Метод витягуємо назви всіх альбомів
def getAlbumsTitle(login, password):
    session = vk.AuthSession(scope='photos', app_id='5677795', user_login=login, user_password=password)
    vkApi = vk.API(session, v='5.62')
    albums = vkApi.photos.getAlbums()
    return session, albums


# Метод створювати новий альбом
def createNewAlbum(session, title):
    vkApi = vk.API(session, v='5.62')
    album = vkApi.photos.createAlbum(title=title)
    return album


# Метод загрузки фото
def uploadPhotoToAlbum(session, album_id, dir, textfield, user):
    vkApi = vk.API(session, v='5.62')
    dir = dir.decode('utf-8')
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    if 'Thumbs.db' in files: files.remove('Thumbs.db')  # Тимчасове рішення, треба зробити перевірку щоб додавати в масив тільки фото
    textfield.insert('end', 'Юзер № {} готовит загрузку {} фото\n'.format(user[0], len(files)))
    textfield.see('end')

    for f in files:
        upload_url = vkApi.photos.getUploadServer(album_id=album_id)
        fil = os.path.join(dir, f)
        fil = os.path.normpath(fil)
        r = requests.post(upload_url['upload_url'], files={'photo': open(fil, "rb")})
        params = {'server': r.json()['server'], 'photos_list': r.json()['photos_list'], 'hash': r.json()['hash'], 'album_id': album_id}
        vkApi.photos.save(**params)
        time.sleep(1)
        textfield.insert('end', 'Юзер № {} загрузил новое фото\n'.format(user[0]))
        textfield.see('end')
        database.addToStatistics(user[9], 'photo')  # Додаємо в статистику


