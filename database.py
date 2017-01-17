#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import sqlite3 as db

from datetime import date, datetime

today = date(2013,11,1)
c = db.connect(database="vkbot")
cu = c.cursor()
try:
    cu.execute("""
          CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login VARCHAR,
            password VARCHAR,
            send_request INTEGER DEFAULT 0,
            max_request INTEGER,
            start_work BOOLEAN DEFAULT 1,
            vk_id INTEGER,
            request_day DATE DEFAULT '2013-11-1',
            all_send_request INTEGER DEFAULT 0,
            name VARCHAR,
            main_page BOOLEAN DEFAULT 0
            );
    """)
except db.DatabaseError, x:
    print "DB Error: ", x
c.commit()
c.close()

# Створюємо таблицю статистики, якщо вона вже є то просто йдемо далі
c = db.connect(database="vkbot")
cu = c.cursor()
try:
    cu.execute("""
          CREATE TABLE statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_name VARCHAR,
            type VARCHAR,
            send_at DATE DEFAULT '2013-11-1'
            );
    """)
except db.DatabaseError, x:
    print "DB Error: ", x
c.commit()
c.close()


# Створюємо таблицю завдань для копіювання, якщо вона вже є то просто йдемо далі
c = db.connect(database="vkbot")
cu = c.cursor()
try:
    cu.execute("""
          CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER,
            text VARCHAR,
            attachments TEXT
            );
    """)
except db.DatabaseError, x:
    print "DB Error: ", x
c.commit()
c.close()


# Метод що змінює start_work на true або false (uid = ід юзера. work = true(1) або false(0)
def updateUserStart(uid, work):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    query = "UPDATE users set start_work=? where ID=?"
    cur.execute(query, (work, uid,))
    con.commit()
    con.close()


# Метод який оновлює вк ІД юзера в базі
def updateVkId(uid, vkID):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    query = "UPDATE users set vk_id=? where ID=?"
    cur.execute(query, (vkID, uid,))
    con.commit()
    con.close()


# Заносимо в базу +1 до к-сть заявок в друзі які акаунт відправив а також +1 до загальної к-сті
def sendRequestCount(ID):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    current = cur.execute('''SELECT send_request, all_send_request  FROM users WHERE id=?''', (ID,))
    query = "UPDATE users set send_request=?, all_send_request=? where id=?"
    for d in current:
        cur.execute(query, (d[0]+1, d[1]+1, ID))
        con.commit()
    con.close()


# Заносимо в базу Максимальну к-сть заявок друзів які можна кинути
def maxRequestSend(ID):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    ran = random.randrange(40, 45)
    query = "UPDATE users set max_request=? where ID=?"
    cur.execute(query, (ran,ID,))
    con.commit()
    con.close()

def sendRequest(ID):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    query = "SELECT send_request, max_request FROM users WHERE id=?"
    send_request = cur.execute(query, (ID,))
    return send_request.fetchone()


# Метод щоб оновити к-сть відправлених заявок на день
def updateUserRequest(ID):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    query = "UPDATE users set send_request=0, request_day=? where ID=?"
    cur.execute(query, (date.today(), ID,))
    con.commit()

# Метод додавання в статистику
def addToStatistics(bot_name, type):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    cur.execute("insert into statistics (bot_name, type, send_at) values (?, ?, ?)",
                (bot_name, type, datetime.now(),))

    con.commit()


# Оновлюємо к-сть відправлених заявок за сьогодні на 0, при старті програми, якщо юзер не відправляв сьогодні заявки
c = db.connect(database="vkbot")
cur = c.cursor()
users = cur.execute("SELECT * FROM users;").fetchall()
c.close()
for i in users:
    if datetime.strptime(i[7], '%Y-%m-%d').date() != date.today():
        updateUserRequest(i[0])
