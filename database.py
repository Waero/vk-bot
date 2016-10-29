#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import sqlite3 as db


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
            vk_id INTEGER
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


# Заносимо в базу +1 до к-сть заявок в друзі які акаунт відправив
def sendRequestCount(ID):
    con = db.connect(database="vkbot")
    cur = con.cursor()
    current = cur.execute('''SELECT send_request FROM users WHERE id=?''', (ID,))
    query = "UPDATE users set send_request=? where id=?"
    for d in current:
        cur.execute(query, (d[0]+1, ID))
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
    ran = random.randrange(40, 45)
    query = "SELECT send_request, max_request FROM users WHERE id=?"
    send_request = cur.execute(query, (ID,))
    return send_request.fetchone()
