#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import tkMessageBox
import Tkinter as tk
import platform
import os

import sys

import vkapi
import worker
import sqlite3 as db
import database
from ConfigParser import SafeConfigParser
from PIL import Image, ImageTk

MAIN_BG='#242424'

# Потрібно щоб не вискакувало вікно на віндовсі при закритті програми
sys.stderr = open('error.log', 'w')
sys.stdout = open('output.log', 'w')

root = tk.Tk()
root.title('Faby')
root.configure(background=MAIN_BG)
root.resizable(width=False, height=False)
root.minsize(width=700, height=500)

top = tk.Frame(root, bg=MAIN_BG)
menu = tk.Frame(root, bg=MAIN_BG)
start = tk.Frame(root, bg=MAIN_BG)
accounts = tk.Frame(root, bg='#e6e6e6')
Sbody = tk.Frame(root, bg='#e6e6e6')
results = tk.Frame(root, bg='#e6e6e6')


# Для Аккаунтів
canvas=tk.Canvas(accounts, bg='#e6e6e6')
listFrame=tk.Frame(canvas, width=550, height=380, bg='#e6e6e6')
scrollb=tk.Scrollbar(accounts, orient="vertical", command=canvas.yview)
scrollb.grid(row=9, rowspan=8, columnspan=100, sticky='nse')  #grid scrollbar in master, but
canvas['yscrollcommand'] = scrollb.set   #attach scrollbar to frameTwo


def AuxscrollFunction(event):
    # You need to set a max size for frameTwo. Otherwise, it will grow as needed, and scrollbar do not act
    canvas.configure(scrollregion=canvas.bbox("all"), width=550, height=380)
    #canvas.configure(scrollregion=canvas.bbox("all"))

listFrame.bind("<Configure>", AuxscrollFunction)
canvas.create_window((10,10),window=listFrame, anchor='w')
canvas.grid(row=8, rowspan=10, column=0, columnspan=100, sticky='w')

# Для Результатів
r_canvas=tk.Canvas(results, bg='#e6e6e6')
r_listFrame=tk.Frame(r_canvas, width=550, height=380, bg='#e6e6e6')
r_scrollb=tk.Scrollbar(results, orient="vertical", command=r_canvas.yview)
r_scrollb.grid(row=9, rowspan=8, columnspan=100, sticky='nse')  #grid scrollbar in master, but
r_canvas['yscrollcommand'] = r_scrollb.set   #attach scrollbar to frameTwo


def r_AuxscrollFunction(event):
    # You need to set a max size for frameTwo. Otherwise, it will grow as needed, and scrollbar do not act
    r_canvas.configure(scrollregion=r_canvas.bbox("all"), width=550, height=380)
    #canvas.configure(scrollregion=canvas.bbox("all"))

r_listFrame.bind("<Configure>", r_AuxscrollFunction)
r_canvas.create_window((10,10),window=r_listFrame, anchor='w')
r_canvas.grid(row=8, rowspan=10, column=0, columnspan=100, sticky='w')

    #создаем виджет text для логіровання на main скріні
textfield = tk.Text(start, width=84, height=22,bg='#e6e6e6')
textfield.place(x=0,y=0)


# Кнопки в меню (різні скріни при кліку)
class MainWindowBtn:
    def __init__(self):
        self.process_img_stun = True
        self.acount_img_stun = False
        self.settings_img_stun = False
        self.results_img_stun = False
    # Картинки на кнопки
        self.start_photo = tk.PhotoImage(file="start_default.png")
        self.start_photo1 = tk.PhotoImage(file="start_hover.png")
        self.stop_default_photo = tk.PhotoImage(file="stop_default.png")
        self.stop_hover_photo = tk.PhotoImage(file="stop.png")
        self.accounts_on = tk.PhotoImage(file="accounts_on.png")
        self.accounts_off = tk.PhotoImage(file="accounts_off.png")
        self.accounts_active = tk.PhotoImage(file="accoynts_btn_active.png")
        self.process_btn_on = tk.PhotoImage(file="process_on.png")
        self.process_btn_off = tk.PhotoImage(file="process_off.png")
        self.process_btn_active = tk.PhotoImage(file="process_btn_active.png")
        self.settings_btn_on = tk.PhotoImage(file="settings_btn_on.png")
        self.settings_btn_off = tk.PhotoImage(file="settings_btn_off.png")
        self.settings_btn_active = tk.PhotoImage(file="settings_btn_active.png")
        self.results_btn_on = tk.PhotoImage(file="results_btn_on.png")
        self.results_btn_off = tk.PhotoImage(file="results_btn_off.png")
        self.results_btn_active = tk.PhotoImage(file="results_btn_active.png")

    # Кнопка Процес
        self.process_btn = tk.Button(menu,
                                      highlightbackground=MAIN_BG,
                                      highlightcolor=MAIN_BG,
                                      bg='#e6e6e6', activebackground='#e6e6e6',
                                      borderwidth=0,
                                      highlightthickness=0,
                                      image=self.process_btn_active
                                      )
        self.process_btn.bind("<Enter>", lambda event, h=self.process_btn: self.process_img(1, h))
        self.process_btn.bind("<Leave>", lambda event, h=self.process_btn: self.process_img(2, h))

        self.process_btn.bind("<Button-1>", self.openProcess)
        self.process_btn.place(x=0,y=0)
    # Кнопка Аккаунти
        self.accounts_btn = tk.Button(menu,
                                  highlightbackground=MAIN_BG,
                                  highlightcolor=MAIN_BG,
                                  activebackground=MAIN_BG,
                                  bg=MAIN_BG,
                                  borderwidth=0,
                                  highlightthickness=0,
                                  image=self.accounts_off
                             )
        self.accounts_btn.bind("<Enter>", lambda event, h=self.accounts_btn: self.acount_img(1, h))
        self.accounts_btn.bind("<Leave>", lambda event, h=self.accounts_btn: self.acount_img(2, h))

        self.accounts_btn.bind("<Button-1>", self.openAccounts)
        self.accounts_btn.place(x=0, y=40)

    # Кнопка Результат
        self.results_btn = tk.Button(menu,
                                      highlightbackground=MAIN_BG,
                                      highlightcolor=MAIN_BG,
                                      activebackground=MAIN_BG,
                                      bg=MAIN_BG,
                                      borderwidth=0,
                                      highlightthickness=0,
                                      image=self.results_btn_off
                                      )
        self.results_btn.bind("<Enter>", lambda event, h=self.results_btn: self.results_img(1, h))
        self.results_btn.bind("<Leave>", lambda event, h=self.results_btn: self.results_img(2, h))

        self.results_btn.bind("<Button-1>", self.openResults)
        self.results_btn.place(x=0, y=80)

    # Кнопка Настройки
        self.settings_btn = tk.Button(menu,
                                  highlightbackground=MAIN_BG,
                                  highlightcolor=MAIN_BG,
                                  activebackground=MAIN_BG,
                                  bg=MAIN_BG,
                                  borderwidth=0,
                                  highlightthickness=0,
                                  image=self.settings_btn_off
                                  )
        self.settings_btn.bind("<Enter>", lambda event, h=self.settings_btn: self.settings_img(1, h))
        self.settings_btn.bind("<Leave>", lambda event, h=self.settings_btn: self.settings_img(2, h))

        self.settings_btn.bind("<Button-1>", self.openSettings)
        self.settings_btn.place(x=0, y=120)

    # Кнопка старт-бот
        self.start_btn = tk.Button(top,
                                  highlightbackground=MAIN_BG,
                                  highlightcolor=MAIN_BG,
                                  activebackground=MAIN_BG,
                                  borderwidth=0,
                                  highlightthickness=0,
                                  #width=140, height=38,
                                  bg=MAIN_BG, image=self.start_photo)
        self.start_btn.bind("<Button-1>", self.startBot)
        self.start_btn.bind("<Enter>", lambda event, h=self.start_btn: h.configure(bg=MAIN_BG, image=self.start_photo1))
        self.start_btn.bind("<Leave>", lambda event, h=self.start_btn: h.configure(bg=MAIN_BG, image=self.start_photo))
        self.start_btn.place(x=530, y=5)

    # Кнопка стоп-бот
        self.stop_btn = tk.Button(top,
                                   highlightbackground=MAIN_BG,
                                   highlightcolor=MAIN_BG,
                                   activebackground=MAIN_BG,
                                   borderwidth=0,
                                   highlightthickness=0,
                                   # width=140, height=38,
                                   bg=MAIN_BG, image=self.stop_default_photo)
        self.stop_btn.bind("<Button-1>", self.stoptBot)
        self.stop_btn.bind("<Enter>", lambda event, h=self.stop_btn: h.configure(bg=MAIN_BG, image=self.stop_hover_photo))
        self.stop_btn.bind("<Leave>", lambda event, h=self.stop_btn: h.configure(bg=MAIN_BG, image=self.stop_default_photo))

    def acount_img(self, stun, h):
        if self.acount_img_stun == True:
            pass
        else:
            if stun == 1:
                h.configure(bg=MAIN_BG, image=self.accounts_on)
            else:
                h.configure(bg=MAIN_BG, image=self.accounts_off)

    def process_img(self, stun, h):
        if self.process_img_stun == True:
            pass
        else:
            if stun == 1:
                h.configure(bg=MAIN_BG, image=self.process_btn_on)
            else:
                h.configure(bg=MAIN_BG, image=self.process_btn_off)

    def results_img(self, stun, h):
        if self.results_img_stun == True:
            pass
        else:
            if stun == 1:
                h.configure(bg=MAIN_BG, image=self.results_btn_on)
            else:
                h.configure(bg=MAIN_BG, image=self.results_btn_off)

    def settings_img(self, stun, h):
        if self.settings_img_stun == True:
            pass
        else:
            if stun == 1:
                h.configure(bg=MAIN_BG, image=self.settings_btn_on)
            else:
                h.configure(bg=MAIN_BG, image=self.settings_btn_off)

    def openProcess(self, event):
        self.acount_img_stun = False
        self.process_img_stun = True
        self.settings_img_stun = False
        self.results_img_stun = False

        self.process_btn.configure(bg='#e6e6e6', activebackground='#e6e6e6', image=self.process_btn_active)
        self.accounts_btn.configure(image=self.accounts_off, bg=MAIN_BG)
        self.settings_btn.configure(image=self.settings_btn_off, bg=MAIN_BG)
        self.results_btn.configure(image=self.results_btn_off, bg=MAIN_BG)
        Sbody.place_forget()
        accounts.place_forget()
        results.place_forget()
        start.place(x=146, y=100, width=550, height=400)

    def openSettings(self, event):
        self.acount_img_stun = False
        self.process_img_stun = False
        self.settings_img_stun = True
        self.results_img_stun = False

        self.process_btn.configure(image=self.process_btn_off, bg=MAIN_BG)
        self.accounts_btn.configure(image=self.accounts_off, bg=MAIN_BG)
        self.settings_btn.configure(bg='#e6e6e6', activebackground='#e6e6e6', image=self.settings_btn_active)
        self.results_btn.configure(image=self.results_btn_off, bg=MAIN_BG)
        start.place_forget()
        accounts.place_forget()
        results.place_forget()
        Sbody.place(x=146, y=100, width=550, height=400)

    def openAccounts(self, event):
        self.acount_img_stun = True
        self.process_img_stun = False
        self.settings_img_stun = False
        self.results_img_stun = False

        self.process_btn.configure(image=self.process_btn_off, bg=MAIN_BG)
        self.accounts_btn.configure(bg='#e6e6e6', activebackground='#e6e6e6', image=self.accounts_active)
        self.settings_btn.configure(image=self.settings_btn_off, bg=MAIN_BG)
        self.results_btn.configure(image=self.results_btn_off, bg=MAIN_BG)
        start.place_forget()
        Sbody.place_forget()
        results.place_forget()
        accounts.place(x=146, y=100, width=550, height=400)

    def openResults(self, event):
        self.results_img_stun = True
        self.process_img_stun = False
        self.settings_img_stun = False
        self.acount_img_stun = False

        self.results_btn.configure(bg='#e6e6e6', activebackground='#e6e6e6', image=self.results_btn_active)
        self.process_btn.configure(image=self.process_btn_off, bg=MAIN_BG)
        self.accounts_btn.configure(image=self.accounts_off, bg=MAIN_BG)
        self.settings_btn.configure(image=self.settings_btn_off, bg=MAIN_BG)

        Results()
        start.place_forget()
        Sbody.place_forget()
        accounts.place_forget()
        results.place(x=146, y=100, width=550, height=400)

    def startBot(self, event):
        self.start_btn.place_forget()
        green_work_label.place(x=30, y=5)
        self.stop_btn.place(x=530, y=5)
        worker.WORK = True
        textfield.configure(state='normal')
        textfield.delete('1.0', 'end')
        worker.goWork(textfield)

    def stoptBot(self, event):
        self.start_btn.place(x=530, y=5)
        green_work_label.place_forget()
        work_label.place(x=30, y=5)
        self.stop_btn.place_forget()
        worker.WORK = False
        textfield.insert('end', 'Faby припиняє роботу... \n')
        textfield.see('end')
        textfield.configure(state='disabled')


# Поля юзера в Settings
class UserFields:
    def __init__(self):

# Виводимо час для рандому
        tk.Label(Sbody, text='Время задержки в секундах', bg='#e6e6e6').grid(row=0, column=4, columnspan=3)
        tk.Label(Sbody, text=' от : ', bg='#e6e6e6').grid(row=1, column=3)
        self.min_time = tk.Entry(Sbody, width=10)
        self.min_time.grid(row=1, column=4)
        tk.Label(Sbody, text=' до : ', bg='#e6e6e6').grid(row=1, column=5)
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
                # config.add_section('main')
            config.set('main', 'max', self.max_time.get())
            config.set('main', 'min', self.min_time.get())

            with open('config.ini', 'w') as f:
                config.write(f)


# Виводимо список людей які є в базі за допомогою цикла в Аккаунти
class Accounts:
    def __init__(self):
        self.login = tk.Label(accounts, text='Логин', bg='#e6e6e6')
        self.loginField = tk.Entry(accounts)
        self.password = tk.Label(accounts, text='Пароль', bg='#e6e6e6')
        self.passwordField = tk.Entry(accounts)
        self.but = tk.Button(accounts,
                             text="Добавить",
                             width=8, height=2,
                             bg="#09380a", fg="white")
        self.but.bind("<Button-1>", self.add_user)
        self.login.grid(row=0)
        self.loginField.grid(row=0, column=1)
        self.password.grid(row=1)
        self.passwordField.grid(row=1, column=1)
        self.but.grid(row=0, rowspan=2, column=2)

        con = db.connect(database="vkbot")
        cur = con.cursor()
        self.id = 6

        # Тут шапка
        tk.Label(listFrame, text='  ', bg='#e6e6e6').grid(row=3, column=0, sticky='w')
        tk.Label(listFrame, text='ID', bg='#e6e6e6').grid(row=4, column=0, padx=15, sticky='w')
        tk.Label(listFrame,  text='Логин', bg='#e6e6e6').grid(row=4, column=1, padx=15, sticky='w')
        tk.Label(listFrame, text='Пароль', bg='#e6e6e6').grid(row=4, column=2, padx=15, sticky='w')
        tk.Label(listFrame, text='Работать?', bg='#e6e6e6').grid(row=4, column=3, padx=15, sticky='w')
        tk.Label(listFrame, text='  ', bg='#e6e6e6').grid(row=5, column=0, sticky='w')

        # Тут формуємо таблицю з усіх юзерів що є у базі
        for i in cur.execute("SELECT * FROM users;"):
            tk.Label(listFrame, text=str(i[0]), bg='#e6e6e6').grid(row=self.id, column=0, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[1]), bg='#e6e6e6').grid(row=self.id, column=1, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[2]), bg='#e6e6e6').grid(row=self.id, column=2, padx=15, sticky='w')
            tk.Label(listFrame, text=str(i[3]), bg='#e6e6e6').grid(row=self.id, column=3, padx=15, sticky='w')
            if i[5] == 1:
                text = 'Да'
            else:
                text = 'Нет'
            but = tk.Button(listFrame, text=text, bg='#e6e6e6')
            but.grid(row=self.id, column=3, padx=15, sticky='w')
            but.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: self.change(event, uid, but))
            self.id = self.id+1

    def change(self, event, uid, but):
        if but.config('text')[-1] == u'Да':
            database.updateUserStart(uid, 0)
            but.config(text=u'Нет')
        else:
            database.updateUserStart(uid, 1)
            but.config(text=u'Да')

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
            but = tk.Button(listFrame, text='Да', bg='#e6e6e6')
            but.grid(row=self.id, column=3, padx=15, sticky='w')
            but.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: self.change(event, uid, but))
            self.id = self.id+1
        con.close()


class Results:
    def __init__(self):
        con = db.connect(database="vkbot")
        cur = con.cursor()
        self.r_id = 6

        # Тут шапка
        tk.Label(r_listFrame, text='  ', bg='#e6e6e6').grid(row=3, column=0, sticky='w')
        tk.Label(r_listFrame, text='ID', bg='#e6e6e6').grid(row=4, column=0, padx=15, sticky='w')
        tk.Label(r_listFrame,  text='Аккаунт', bg='#e6e6e6').grid(row=4, column=1, padx=15, sticky='w')
        tk.Label(r_listFrame, text='Сегодня', bg='#e6e6e6').grid(row=4, column=2, padx=15, sticky='w')
        tk.Label(r_listFrame, text='За все время', bg='#e6e6e6').grid(row=4, column=3, padx=15, sticky='w')
        tk.Label(r_listFrame, text='  ', bg='#e6e6e6').grid(row=5, column=0, sticky='w')

        # Тут формуємо таблицю з усіх юзерів що є у базі
        for i in cur.execute("SELECT * FROM users;"):
            tk.Label(r_listFrame, text=str(i[0]), bg='#e6e6e6').grid(row=self.r_id, column=0, padx=15, sticky='w')
            tk.Label(r_listFrame, text=str(i[1]), bg='#e6e6e6').grid(row=self.r_id, column=1, padx=15, sticky='w')
            tk.Label(r_listFrame, text=str(i[3]), bg='#e6e6e6').grid(row=self.r_id, column=2, padx=15, sticky='w')
            tk.Label(r_listFrame, text=str(i[8]), bg='#e6e6e6').grid(row=self.r_id, column=3, padx=15, sticky='w')

            self.r_id = self.r_id+1


if __name__ == "__main__":
    MainWindowBtn()
    UserFields()
    Accounts()
    Results()
    top.place(x=0, y=0, width=700, height=100)
    menu.place(x=0, y=100, width=150, height=400)
    start.place(x=146, y=100, width=550, height=400)

    # Червона кнопка
    image = Image.open("activity_off.png")
    work = ImageTk.PhotoImage(image)
    work_label = tk.Label(top, image=work, width=450, height=80, bg=MAIN_BG, bd=0)
    work_label.place(x=30, y=5)

    # Зелена кнопка
    green_work = tk.PhotoImage(file="activity_on.png")
    green_work_label = tk.Label(top, image=green_work, width=450, height=80,bd=0, bg=MAIN_BG)


    root.mainloop()
