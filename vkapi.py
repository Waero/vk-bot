#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vk


# Метод створює сесію і витягує друзів користувача
def getFriendsAndSession(login, password):
    session = vk.AuthSession(scope='friends, messages, offline', app_id='5677795', user_login=login, user_password=password)
    vkApi = vk.API(session)
    uf = vkApi.friends.get(order='hints')
    # uf - cписок всіх друзів
    # session - Сесія юзера
    return uf, session


# Метод витягує id користувача
def getVkId(login, password):
    session = vk.AuthSession(scope='friends, offline', app_id='5677795', user_login=login, user_password=password)
    vkApi = vk.API(session)
    vk_id = vkApi.users.get()
    return vk_id


# Метод витягує профіль юзера по ID
def getUser(session,id):
    vkApi = vk.API(session)
    u = vkApi.users.get(user_ids=id, fields='last_seen')
    return u


# Метод витягує друзів друга по ID
def getFriends(session, id):
    vkApi = vk.API(session)
    u = vkApi.friends.get(user_id=id, order='hints')
    return u


# Метод витягує спільних друзів карент юзера і юзера (ID)
def getMutalFriends(session, id):
    vkApi = vk.API(session)
    mutal_friends = vkApi.friends.getMutual(target_uid=id)
    return mutal_friends


# Метод відправляємо заявку в друзі (ID)
def addToFriend(session, id):
    vkApi = vk.API(session)
    added_friend = vkApi.friends.add(user_id=id)
    return added_friend


def addToFriendCaptcha(session, id, captcha_sid, captcha_key):
    vkApi = vk.API(session)
    added_friend = vkApi.friends.add(user_id=id, captcha_sid=captcha_sid, captcha_key=captcha_key)
    return added_friend


# Метод витягує кому вже відправлялись заявки
def getRequests(session):
    vkApi = vk.API(session)
    sended_request = vkApi.friends.getRequests(out=1)
    return sended_request


# Метод витягує нові повідомлення
def getMessages(session):
    vkApi = vk.API(session, v='5.60')
    new_messages = vkApi.messages.getDialogs(unread=1)
    return new_messages

def sendMessage(session, f_id, message):
    vkApi = vk.API(session, v='5.60')
    send_messages = vkApi.messages.send(user_id=f_id, message=message)
