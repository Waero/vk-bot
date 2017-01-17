# -*- coding: utf-8 -*-
import database
import sqlite3 as db
import requests



def sendStatistics():
    con = db.connect(database="vkbot")
    cur = con.cursor()
    for i in cur.execute("SELECT * FROM statistics;"):
        requests.post("http://127.0.0.1/faby/web/statistics/update", data={'Statistics[user_id]': 1,
                                                                           'Statistics[bot_name]': i[1],
                                                                           'Statistics[type]': i[2],
                                                                           'Statistics[send_at]': i[3],})

        cur.execute("DELETE FROM statistics WHERE id=?;", (i[0],))
        con.commit()

    con.close()
