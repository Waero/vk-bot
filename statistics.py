# -*- coding: utf-8 -*-
import json
from ConfigParser import SafeConfigParser

import database
import sqlite3 as db
import requests
import Tkinter as tk


class Statistics:
    def __init__(self, root):
        self.root = root
        self.root.bind('d'+'l', self.printl)

    def printl(self, event):
        root = self.root
        LoginDialog(root)


class LoginDialog:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.login_frame = tk.Frame(self.top)
        self.login_label = tk.Label(self.login_frame, text="Логин:").grid(row=0, column=1)
        self.pass_label = tk.Label(self.login_frame, text="Пароль:").grid(row=1, column=1)

        self.e1 = tk.Entry(self.login_frame)
        self.e2 = tk.Entry(self.login_frame)
        self.e1.grid(row=0, column=2, columnspan=2)
        self.e2.grid(row=1, column=2, columnspan=2)

        self.log_btn = tk.Button(self.login_frame, text="Логин", command=self.ok)
        self.log_btn.grid(row=2, column=2)
        self.login_frame.pack()

    def ok(self):
        response = requests.post("http://localhost:8000/auth/botLogin",
                      data={'email': self.e1.get(),
                            'password': self.e2.get(),
                            })

        json_data = json.loads(response.text)

        # Зберігаємо в конфіг значення
        config = SafeConfigParser()
        config.read('config.ini')
        config.set('stat', 'bot_token', json_data['bot_token'])

        with open('config.ini', 'w') as f:
            config.write(f)

        self.login_frame.pack_forget()
        self.sinc_frame = tk.Frame(self.top)
        self.sinc = tk.Button(self.sinc_frame, text="Отправить статистику", command=self.sendStatistics)
        self.sinc.grid(row=2, column=2)
        self.sinc_frame.pack()

    def sendStatistics(self):
        config = SafeConfigParser()
        config.read('config.ini')
        bot_token = config.get('stat', 'bot_token')
        con = db.connect(database="vkbot")
        cur = con.cursor()
        for i in cur.execute("SELECT * FROM statistics;"):
            requests.post("http://localhost:8000/statistics", data={'bot_token': bot_token,
                                                                        'bot_name': i[1],
                                                                        'type': i[2],
                                                                        'send_at': i[3], })

        # cur.execute("DELETE FROM statistics WHERE id=?;", (i[0],))
        # con.commit()

        con.close()