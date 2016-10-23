#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tkMessageBox
import Tkinter as tk
import platform
import os
import worker
import sqlite3 as db
import database


root = tk.Tk()
root.title('vk-bot')
root.resizable(width=False, height=False)
root.minsize(width=700, height=500)

menu = tk.Frame(root, width=700, height=27)
body = tk.Frame(root, width=700, height=300)
bottom = tk.Frame(root, width=700, height=150)
Sbody = tk.Frame(root, width=700, height=300)

    #создаем виджет text для логіровання на main скріні

textfield = tk.Text(body, height=20,width=100,)
textfield.pack()

# Кнопки в меню
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
        self.but.pack()

    def startBot(self, event):
        print "start"
        worker.goWork(textfield)


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

#Виводимо список людей які є в базі за допомогою цикла
        con = db.connect(database="vkbot")
        cur = con.cursor()
        id = 3
        for i in cur.execute("SELECT * FROM users;"):
            tk.Label(Sbody, text=str(i[0]) + ' ' + i[1] + ' ' + i[2]).grid(row=id, column=0, columnspan=3, sticky='w')
            id = id+1

#Додаємо нового юзера в базу
    def add_user(self, event):
        print "user_added"
        con = db.connect(database="vkbot")
        cur = con.cursor()

        login = self.loginField.get()
        password = self.passwordField.get()

        # This is the qmark style:
        cur.execute("insert into users (login,password) values (?, ?)", (login, password))
        con.commit()
        con.close()
        # Виводимо алерт що юзера додано в базу
        tkMessageBox.showinfo(
            "Updated",
            "User {} is added".format(login)
        )
        # Очищаємо поле для ввода логіна і пароля
        self.loginField.delete("0", "end")
        self.passwordField.delete("0", "end")


if __name__ == "__main__":
    MainWindowBtn()
    ButStart()
    UserFields()
    menu.grid(row=1, sticky='W')
    body.grid(row=2)
    bottom.grid(row=3)
    root.mainloop()
