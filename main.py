#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tkMessageBox
import Tkinter as tk
import platform
import os

import vkapi
import worker
import sqlite3 as db
import database
from ConfigParser import SafeConfigParser



root = tk.Tk()
root.title('vk-bot')
root.resizable(width=False, height=False)
root.minsize(width=700, height=500)

menu = tk.Frame(root, width=700, height=27)
body = tk.Frame(root, width=700, height=300)
bottom = tk.Frame(root, width=700, height=150)
Sbody = tk.Frame(root,  width=700, height=300)

canvas=tk.Canvas(Sbody)
listFrame=tk.Frame(canvas, width=700, height=380)
scrollb=tk.Scrollbar(Sbody, orient="vertical", command=canvas.yview)
scrollb.grid(row=8, rowspan=10, columnspan=100, sticky='nse')  #grid scrollbar in master, but
canvas['yscrollcommand'] = scrollb.set   #attach scrollbar to frameTwo


def AuxscrollFunction(event):
    # You need to set a max size for frameTwo. Otherwise, it will grow as needed, and scrollbar do not act
    canvas.configure(scrollregion=canvas.bbox("all"), width=700, height=380)
    #canvas.configure(scrollregion=canvas.bbox("all"))

listFrame.bind("<Configure>", AuxscrollFunction)
canvas.create_window((10,10),window=listFrame, anchor='w')

#scrollb.grid_forget()                         # Forget scrollbar because the number of pieces remains undefined by the user. But this not destroy it. It will be "remembered" later.
canvas.grid(row=8, rowspan=10, column=0, columnspan=100, sticky='w')

    #создаем виджет text для логіровання на main скріні
textfield = tk.Text(body, height=20,width=100)
textfield.pack()

# Кнопки в меню (різні скріни при кліку)
class MainWindowBtn:
    def __init__(self):
        #butfont = font.Font(family='Ubuntu', size=10)
        self.mainb = tk.Button(menu,
                          text="Main",
                          width=8, height=1,
                          bg="green", fg="white")

        self.mainb.bind("<Button-1>", self.openMain)
        self.mainb.grid(row=1, column=1)
        self.settingb = tk.Button(menu,
                             text="Settings",
                             width=8, height=1,
                             bg="green", fg="white")

        self.settingb.bind("<Button-1>", self.openSettings)
        self.settingb.grid(row=1, column=2)

    def openMain(self, event):
        Sbody.grid_forget()
        body.grid(row=2)
        bottom.grid(row=3)

    def openSettings(self, event):
        body.grid_forget()
        bottom.grid_forget()
        Sbody.grid(row=2)


# Кнопка старт-бот
class ButStart:
    def __init__(self):
        self.but = tk.Button(bottom,
                            text="Start Bot",
                            width=12, height=3,
                            bg="green", fg="white")
        self.but.bind("<Button-1>", self.startBot)
        self.but.grid()

    def startBot(self, event):
        print "start"
        worker.goWork(textfield)
        self.but.grid_forget()


# Поля юзера в Settings
class UserFields:
    def __init__(self):
        self.login = tk.Label(Sbody, text='Login')
        self.loginField = tk.Entry(Sbody)
        self.password = tk.Label(Sbody, text='Password')
        self.passwordField = tk.Entry(Sbody)
        self.but = tk.Button(Sbody,
                            text="Add User",
                            width=8, height=2,
                            bg="green", fg="white")
        self.but.bind("<Button-1>", self.add_user)
        self.login.grid(row=0)
        self.loginField.grid(row=0, column=1)
        self.password.grid(row=1)
        self.passwordField.grid(row=1, column=1)
        self.but.grid(row=0, rowspan=2, column=2)

# Виводимо час для рандому
        tk.Label(Sbody, text='Random Time in seconds').grid(row=0, column=4, columnspan=3)
        tk.Label(Sbody, text=' min : ').grid(row=1, column=3)
        self.min_time = tk.Entry(Sbody, width=10)
        self.min_time.grid(row=1, column=4)
        tk.Label(Sbody, text=' max : ').grid(row=1, column=5)
        self.max_time = tk.Entry(Sbody, width=10)
        self.max_time.grid(row=1, column=6)
        #self.image = tk.PhotoImage(file="123.png")
        self.edit_btn = tk.Button(Sbody,
                                  text='Edit',
                                  width=7, height=2,
                                  bg='green', fg="white")
        self.edit_btn.bind("<Button-1>", self.edit_time)
        self.edit_btn.grid(row=0, rowspan=2, column=7)
        # Заповнюємо min і max значеннями з конфіг файла
        config = SafeConfigParser()
        config.read('config.ini')
        max = config.get('main', 'max')
        min = config.get('main', 'min')
        self.min_time.insert(0, min)
        self.max_time.insert(0, max)
        self.min_time.config(state='disabled')
        self.max_time.config(state='disabled')


# Виводимо список людей які є в базі за допомогою цикла
        con = db.connect(database="vkbot")
        cur = con.cursor()
        self.id = 6

        # Тут шапка
        tk.Label(listFrame, text='  ').grid(row=3, column=0, sticky='w')
        tk.Label(listFrame, text='ID').grid(row=4, column=0, padx=15, sticky='w')
        tk.Label(listFrame,  text='Login').grid(row=4, column=1, padx=15, sticky='w')
        tk.Label(listFrame, text='Password').grid(row=4, column=2, padx=15, sticky='w')
        #tk.Label(listFrame, text='Send Request').grid(row=4, column=3, padx=15, sticky='w')
        tk.Label(listFrame, text='Work?').grid(row=4, column=4, padx=15, sticky='w')
        tk.Label(listFrame, text='  ').grid(row=5, column=0, sticky='w')

        # Тут формуємо таблицю з усіх юзерів що є у базі
        for i in cur.execute("SELECT * FROM users;"):
            tk.Label(listFrame, text=str(i[0])).grid(row=self.id, column=0, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[1])).grid(row=self.id, column=1, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[2])).grid(row=self.id, column=2, padx=15, sticky='w')
            #tk.Label(listFrame, text=str(i[3])).grid(row=self.id, column=3, padx=15, sticky='w')
            if i[5] == 1:
                text = 'On'
            else:
                text = 'Off'
            but = tk.Button(listFrame, text=text)
            but.grid(row=self.id, column=4, padx=15, sticky='w')
            but.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: self.change(event, uid, but))
            self.id = self.id+1


    def change(self, event, uid, but):
        if but.config('text')[-1] == 'On':
            database.updateUserStart(uid, 0)
            but.config(text='Off')
        else:
            database.updateUserStart(uid, 1)
            but.config(text='On')



# Метод для кнопки Edit і Save для рандомного часу
    def edit_time(self, event):
        if self.edit_btn.config('text')[-1] == 'Edit':
                self.min_time.config(state='normal')
                self.max_time.config(state='normal')
                self.edit_btn.config(text='Save')
        else:
            self.min_time.config(state='disabled')
            self.max_time.config(state='disabled')
            self.edit_btn.config(text='Edit')
            # Зберігаємо в конфіг значення max i min
            config = SafeConfigParser()
            config.read('config.ini')
            #config.add_section('main')
            config.set('main', 'max', self.max_time.get())
            config.set('main', 'min', self.min_time.get())

            with open('config.ini', 'w') as f:
                config.write(f)


# Метод додавання нового юзера в базу
    def add_user(self, event):
        con = db.connect(database="vkbot")
        cur = con.cursor()

        login = self.loginField.get()
        password = self.passwordField.get()
        vk_id = vkapi.getVkId(login=login, password=password)
        # This is the qmark style:
        cur.execute("insert into users (login, password, vk_id) values (?, ?, ?)", (login, password, vk_id))
        con.commit()
        lastList = cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")

        # Виводимо алерт що юзера додано в базу
        tkMessageBox.showinfo(
            "Updated",
            "User {} is added".format(login)
        )
        # Очищаємо поле для ввода логіна і пароля і додаємо останнього юзера на екран
        self.loginField.delete("0", "end")
        self.passwordField.delete("0", "end")
        for i in lastList:
            tk.Label(listFrame, text=str(i[0])).grid(row=self.id, column=0, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[1])).grid(row=self.id, column=1, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[2])).grid(row=self.id, column=2, padx=15, sticky='w')
            #tk.Label(listFrame, text=str(i[3])).grid(row=self.id, column=3, padx=15, sticky='w')
            but = tk.Button(listFrame, text='On')
            but.grid(row=self.id, column=4, padx=15, sticky='w')
            but.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: self.change(event, uid, but))
            self.id = self.id+1
        con.close()


if __name__ == "__main__":
    MainWindowBtn()
    ButStart()
    UserFields()
    menu.grid(row=1, sticky='W')
    body.grid(row=2)
    bottom.grid(row=3)
    root.mainloop()
