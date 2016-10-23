#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vk


# Метод створює сесію і витягує друзів користувача
def getFriendsAndSession(login, password):
    session = vk.AuthSession(scope='friends, offline', app_id='5677795', user_login=login, user_password=password)
    vkapi = vk.API(session)
    uf = vkapi.friends.get(order='hints')
    # uf - cписок всіх друзів
    # session - Сесія юзера
    return uf, session


# Метод витягує профіль юзера по ID
def getUser(session,id):
    vkapi = vk.API(session)
    u = vkapi.users.get(user_ids=id)
    return u


# Метод витягує друзів друга по ID
def getFriends(session, id):
    vkapi = vk.API(session)
    u = vkapi.friends.get(user_id=id, order='hints')
    return u


# Метод витягує спільних друзів карент юзера і юзера (ID)
def getMutalFriends(session, id):
    vkapi = vk.API(session)
    mutal_friends = vkapi.friends.getMutual(target_uid=id)
    return mutal_friends