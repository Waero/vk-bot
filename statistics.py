# -*- coding: utf-8 -*-
import database
import sqlite3 as db
import requests
from datetime import date, datetime


def sendStatistics():
    con = db.connect(database="vkbot")
    cur = con.cursor()
    for i in cur.execute("SELECT * FROM statistics;"):
        requests.post("http://127.0.0.1/faby/web/statistics/update", data={'Statistics[user_id]': 1,
                                                                           'Statistics[bot_name]': i[1],
                                                                           'Statistics[type]': i[2],
                                                                           'Statistics[send_at]': i[3],})


