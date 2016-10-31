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
root.title('Faby')
root.configure(background='#242424')
root.resizable(width=False, height=False)
root.minsize(width=700, height=500)

top = tk.Frame(root, bg='')
menu = tk.Frame(root, bg='')
start = tk.Frame(root, bg='')
accounts = tk.Frame(root, bg='#e6e6e6')
Sbody = tk.Frame(root, bg='#e6e6e6')

canvas=tk.Canvas(accounts, bg='#e6e6e6')
listFrame=tk.Frame(canvas, width=600, height=380, bg='#e6e6e6')
scrollb=tk.Scrollbar(accounts, orient="vertical", command=canvas.yview)
scrollb.grid(row=9, rowspan=8, columnspan=100, sticky='nse')  #grid scrollbar in master, but
canvas['yscrollcommand'] = scrollb.set   #attach scrollbar to frameTwo


def AuxscrollFunction(event):
    # You need to set a max size for frameTwo. Otherwise, it will grow as needed, and scrollbar do not act
    canvas.configure(scrollregion=canvas.bbox("all"), width=600, height=380)
    #canvas.configure(scrollregion=canvas.bbox("all"))

listFrame.bind("<Configure>", AuxscrollFunction)
canvas.create_window((10,10),window=listFrame, anchor='w')

#scrollb.grid_forget()                         # Forget scrollbar because the number of pieces remains undefined by the user. But this not destroy it. It will be "remembered" later.
canvas.grid(row=8, rowspan=10, column=0, columnspan=100, sticky='w')

    #создаем виджет text для логіровання на main скріні
textfield = tk.Text(start, width=84, height=22,bg='#e6e6e6')
textfield.place(x=0,y=0)

# Кнопки в меню (різні скріни при кліку)
class MainWindowBtn:
    def __init__(self):
        #butfont = font.Font(family='Ubuntu', size=10)
        self.start = tk.Button(menu,
                          text="Start",
                          width=10, height=2,
                          bg='#e6e6e6', fg='black')

        self.start.bind("<Button-1>", self.openMain)
        self.start.place(x=0,y=0)
        self.accounts = tk.Button(menu,
                             text="Accounts",
                             width=10, height=2,
                             bg='black', fg='white')

        self.accounts.bind("<Button-1>", self.openAccounts)
        self.accounts.place(x=0,y=40)
        self.sett_photo = tk.PhotoImage(file="123.png")
        self.settings = tk.Button(top,
                                  highlightbackground='#242424',
                                  highlightcolor ='#242424',
                                  borderwidth=0,
                                  highlightthickness=0,
                                  #text="Settings",
                                  width=140, height=38,
                                  bg='black', fg='white', image=self.sett_photo)
        self.settings.bind("<Button-1>", self.openSettings)
        self.settings.place(x=530,y=20)

    def openMain(self, event):
        self.start.configure(bg='#e6e6e6', fg='black')
        self.accounts.configure(bg='black', fg='white')
        self.settings.configure(bg='black', fg='white')
        Sbody.place_forget()
        accounts.place_forget()
        start.place(x=100, y=100, width=600, height=400)


    def openSettings(self, event):
        self.start.configure(bg='black', fg='white')
        self.accounts.configure(bg='black', fg='white')
        self.settings.configure(bg='#e6e6e6', fg='black')
        start.place_forget()
        accounts.place_forget()
        Sbody.place(x=100, y=100, width=600, height=400)

    def openAccounts(self, event):
        self.start.configure(bg='black', fg='white')
        self.accounts.configure(bg='#e6e6e6', fg='black')
        self.settings.configure(bg='black', fg='white')
        start.place_forget()
        Sbody.place_forget()
        accounts.place(x=100, y=100, width=600, height=400)


# Кнопка старт-бот
class ButStart:
    def __init__(self):
        self.but = tk.Button(start,
                            text="Start Bot",
                            width=12, height=3,
                            bg="#09380a", fg="white")
        self.but.bind("<Button-1>", self.startBot)
        self.but.place(relx=0.5, rely=1.0, anchor='s')

    def startBot(self, event):
        print "start"
        worker.goWork(textfield)
        self.but.place_forget()


# Поля юзера в Settings
class UserFields:
    def __init__(self):
        self.login = tk.Label(accounts, text='Login', bg='#e6e6e6')
        self.loginField = tk.Entry(accounts)
        self.password = tk.Label(accounts, text='Password', bg='#e6e6e6')
        self.passwordField = tk.Entry(accounts)
        self.but = tk.Button(accounts,
                            text="Add User",
                            width=8, height=2,
                            bg="#09380a", fg="white")
        self.but.bind("<Button-1>", self.add_user)
        self.login.grid(row=0)
        self.loginField.grid(row=0, column=1)
        self.password.grid(row=1)
        self.passwordField.grid(row=1, column=1)
        self.but.grid(row=0, rowspan=2, column=2)

# Виводимо час для рандому
        tk.Label(Sbody, text='Random Time in seconds', bg='#e6e6e6').grid(row=0, column=4, columnspan=3)
        tk.Label(Sbody, text=' min : ', bg='#e6e6e6').grid(row=1, column=3)
        self.min_time = tk.Entry(Sbody, width=10)
        self.min_time.grid(row=1, column=4)
        tk.Label(Sbody, text=' max : ', bg='#e6e6e6').grid(row=1, column=5)
        self.max_time = tk.Entry(Sbody, width=10)
        self.max_time.grid(row=1, column=6)
        #self.image = tk.PhotoImage(file="123.png")
        self.edit_btn = tk.Button(Sbody,
                                  text='Edit',
                                  width=7, height=2,
                                  bg='#09380a', fg="white")
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
        tk.Label(listFrame, text='  ', bg='#e6e6e6').grid(row=3, column=0, sticky='w')
        tk.Label(listFrame, text='ID', bg='#e6e6e6').grid(row=4, column=0, padx=15, sticky='w')
        tk.Label(listFrame,  text='Login', bg='#e6e6e6').grid(row=4, column=1, padx=15, sticky='w')
        tk.Label(listFrame, text='Password', bg='#e6e6e6').grid(row=4, column=2, padx=15, sticky='w')
        #tk.Label(listFrame, text='Send Request', bg='#e6e6e6').grid(row=4, column=3, padx=15, sticky='w')
        tk.Label(listFrame, text='Work?', bg='#e6e6e6').grid(row=4, column=4, padx=15, sticky='w')
        tk.Label(listFrame, text='  ', bg='#e6e6e6').grid(row=5, column=0, sticky='w')

        # Тут формуємо таблицю з усіх юзерів що є у базі
        for i in cur.execute("SELECT * FROM users;"):
            tk.Label(listFrame, text=str(i[0]), bg='#e6e6e6').grid(row=self.id, column=0, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[1]), bg='#e6e6e6').grid(row=self.id, column=1, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[2]), bg='#e6e6e6').grid(row=self.id, column=2, padx=15, sticky='w')
            #tk.Label(listFrame, text=str(i[3]), bg='#e6e6e6').grid(row=self.id, column=3, padx=15, sticky='w')
            if i[5] == 1:
                text = 'On'
            else:
                text = 'Off'
            but = tk.Button(listFrame, text=text, bg='#e6e6e6')
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
            tk.Label(listFrame, text=str(i[0]), bg='#e6e6e6').grid(row=self.id, column=0, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[1]), bg='#e6e6e6').grid(row=self.id, column=1, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[2]), bg='#e6e6e6').grid(row=self.id, column=2, padx=15, sticky='w')
            #tk.Label(listFrame, text=str(i[3]), bg='#e6e6e6').grid(row=self.id, column=3, padx=15, sticky='w')
            but = tk.Button(listFrame, text='On', bg='#e6e6e6')
            but.grid(row=self.id, column=4, padx=15, sticky='w')
            but.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: self.change(event, uid, but))
            self.id = self.id+1
        con.close()


if __name__ == "__main__":
    MainWindowBtn()
    ButStart()
    UserFields()
    top.place(x=0, y=0, width=700, height=100)
    menu.place(x=0, y=100, width=100, height=400)
    start.place(x=100, y=100, width=600, height=400)

    root.mainloop()
