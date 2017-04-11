# -*- coding: utf-8 -*-
import Tkinter as tk
from ConfigParser import SafeConfigParser
from PIL import Image, ImageTk
import sqlite3 as db

import vk

import database
import vkapi
import tkMessageBox


# Виводимо список людей які є в базі за допомогою цикла в Аккаунти
class Accounts:

    def __init__(self, accounts):
        self.accounts = accounts
        # Для Аккаунтів
        canvas = tk.Canvas(accounts, bg='#e6e6e6')
        self.listFrame = tk.Frame(canvas, width=550, height=380, bg='#e6e6e6')
        scrollb = tk.Scrollbar(accounts, orient="vertical", command=canvas.yview)
        scrollb.grid(row=9, rowspan=8, columnspan=100, sticky='nse')  # grid scrollbar in master, but
        canvas['yscrollcommand'] = scrollb.set  # attach scrollbar to frameTwo

        def AuxscrollFunction(event):
            # You need to set a max size for frameTwo. Otherwise, it will grow as needed, and scrollbar do not act
            canvas.configure(scrollregion=canvas.bbox("all"), width=550, height=350)
            # canvas.configure(scrollregion=canvas.bbox("all"))

        self.listFrame.bind("<Configure>", AuxscrollFunction)
        canvas.create_window((10, 10), window=self.listFrame, anchor='w')
        canvas.grid(row=8, rowspan=10, column=0, columnspan=100, sticky='w')

        self.add_akk_btn_off = ImageTk.PhotoImage(Image.open("img/add_akk_btn_off.png"))
        self.add_akk_btn_on = ImageTk.PhotoImage(Image.open("img/add_akk_btn_on.png"))
        self.add_akk_btn_click = ImageTk.PhotoImage(Image.open("img/add_akk_btn_click.png"))
        self.delete_btn_off = ImageTk.PhotoImage(Image.open("img/delete_btn1.png"))
        self.delete_btn_on = ImageTk.PhotoImage(Image.open("img/delete_btn2.png"))
        self.edit_user_btn_off = ImageTk.PhotoImage(Image.open("img/edit_user_off.png"))
        self.edit_user_btn_on = ImageTk.PhotoImage(Image.open("img/edit_user_on.png"))
        self.work_btn_off = ImageTk.PhotoImage(Image.open("img/work_off.png"))
        self.work_btn_on = ImageTk.PhotoImage(Image.open("img/work_on.png"))

        self.login = tk.Label(accounts, text='Логин', bg='#e6e6e6')
        self.loginField = tk.Entry(accounts)
        self.password = tk.Label(accounts, text='Пароль', bg='#e6e6e6')
        self.passwordField = tk.Entry(accounts)

        self.add_akk_btn = tk.Button(accounts,
                                      #highlightbackground='#e6e6e6',
                                      #highlightcolor='#e6e6e6',
                                      #activebackground='#e6e6e6',
                                      bg='#e6e6e6',
                                      borderwidth=0,
                                      highlightthickness=0,
                                      image=self.add_akk_btn_off
                                      )
        self.add_akk_btn.bind("<Enter>", lambda event, h=self.add_akk_btn: h.configure(bg='#e6e6e6', image=self.add_akk_btn_click))
        self.add_akk_btn.bind("<Leave>", lambda event, h=self.add_akk_btn: h.configure(bg='#e6e6e6', image=self.add_akk_btn_off))
        self.add_akk_btn.bind("<Button-1>", self.add_user)

        self.login.grid(row=0)
        self.loginField.grid(row=0, column=1)
        self.password.grid(row=1)
        self.passwordField.grid(row=1, column=1)
        self.add_akk_btn.grid(row=0, rowspan=2, column=2, padx=15)

        con = db.connect(database="vkbot")
        cur = con.cursor()
        self.id = 6

        # Тут шапка
        tk.Label(self.listFrame, text='  ', bg='#e6e6e6').grid(row=3, column=0, sticky='w')
        tk.Label(self.listFrame, text='ID', bg='#e6e6e6').grid(row=4, column=0, padx=15, sticky='w')
        tk.Label(self.listFrame,  text='Аккаунт', bg='#e6e6e6').grid(row=4, column=1, padx=15, sticky='w')
        tk.Label(self.listFrame, text='Работать?', bg='#e6e6e6').grid(row=4, column=2, padx=15, sticky='w')
        tk.Label(self.listFrame, text='Опции', bg='#e6e6e6').grid(row=4, column=3, columnspan=2, padx=15)
        tk.Label(self.listFrame, text='Главная', bg='#e6e6e6').grid(row=4, column=5, columnspan=1, padx=15)
        tk.Label(self.listFrame, text='  ', bg='#e6e6e6').grid(row=5, column=0, sticky='w')

        # Тут формуємо таблицю з усіх юзерів що є у базі
        self.main_page = tk.IntVar()

        for i in cur.execute("SELECT * FROM users;"):
            tk.Label(self.listFrame, text=str(i[0]), bg='#e6e6e6').grid(row=self.id, column=0, padx=15, sticky='w')
            tk.Label(self.listFrame, text=i[9], bg='#e6e6e6').grid(row=self.id, column=1, padx=15, sticky='w')
            if i[5] == 1:
                image = self.work_btn_on
                text = 'Yes'
            else:
                image = self.work_btn_off
                text = 'No'
            but = tk.Button(self.listFrame, image=image, text=text, bg='#e6e6e6', borderwidth=0, highlightthickness=0)
            but.grid(row=self.id, column=2, padx=15)
            but.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: self.change(event, uid, but))
        # Кнопки Редагувати і Видалити аккаунт
            edit_btn = tk.Button(self.listFrame, image=self.edit_user_btn_off,borderwidth=0,highlightthickness=0,  bg='#e6e6e6')
            edit_btn.bind("<Enter>", lambda event, h=edit_btn: h.configure(image=self.edit_user_btn_on))
            edit_btn.bind("<Leave>", lambda event, h=edit_btn: h.configure(image=self.edit_user_btn_off))
            edit_btn.grid(row=self.id, column=3, padx=15, sticky='w')
            edit_btn.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: EditUserDialog(parent=self.listFrame, uid=uid, accounts=accounts))
            delete_btn = tk.Button(self.listFrame, image=self.delete_btn_off,borderwidth=0,
                                      highlightthickness=0,  bg='#e6e6e6')
            delete_btn.bind("<Enter>", lambda event, h=delete_btn: h.configure(image=self.delete_btn_on))
            delete_btn.bind("<Leave>", lambda event, h=delete_btn: h.configure(image=self.delete_btn_off))
            delete_btn.grid(row=self.id, column=4, padx=15, sticky='we')
            delete_btn.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: self.deleteUser(uid=uid))
        # Radiobutton для головної сторінки
            tk.Radiobutton(self.listFrame, variable=self.main_page, value=i[0], borderwidth=0, bg='#e6e6e6',
                           highlightthickness=0, command=self.markAsMainPage).grid(row=self.id, column=5, padx=15,
                                                                                   sticky='we')
            if i[10] == 1:
                self.main_page.set(i[0])

            self.id = self.id+1

    def change(self, event, uid, but):
        if but.config('text')[-1] == 'Yes':
            database.updateUserStart(uid, 0)
            but.config(text='No', image=self.work_btn_off)

        else:
            database.updateUserStart(uid, 1)
            but.config(text='Yes', image=self.work_btn_on)

    def deleteUser(self, uid):
        con = db.connect(database="vkbot")
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE id=?", (uid,))
        con.commit()
        con.close()
        for child in self.listFrame.winfo_children():
            child.destroy()
        Accounts(self.accounts)

# Метод додавання нового юзера в базу
    def add_user(self, event):
        con = db.connect(database="vkbot")
        cur = con.cursor()

        login = self.loginField.get().strip()
        password = self.passwordField.get().strip()
        try:
            vk_id = vkapi.get_vk_id(login=login, password=password)
            uname = vk_id[0]['first_name'] + ' ' + vk_id[0]['last_name']
            # This is the qmark style:
            cur.execute("insert into users (login, password, vk_id, name) values (?, ?, ?, ?)",
                        (login, password, vk_id[0]['id'], uname))
            con.commit()
            lastList = cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")

            # Виводимо алерт що юзера додано в базу
            tkMessageBox.showinfo(
                "Updated",
                "Аккаунт {} успешно додан".format(uname.encode('utf-8'))
            )
            # Додаємо останнього юзера на екран
            for i in lastList:
                tk.Label(self.listFrame, text=str(i[0]), bg='#e6e6e6').grid(row=self.id, column=0, padx=15, sticky='w')
                tk.Label(self.listFrame, text=i[9], bg='#e6e6e6').grid(row=self.id, column=1, padx=15, sticky='w')
                but = tk.Button(self.listFrame, text='Yes',image=self.work_btn_on, bg='#e6e6e6', borderwidth=0, highlightthickness=0)
                but.grid(row=self.id, column=2, padx=15)
                but.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: self.change(event, uid, but))
                # Кнопки Редагувати і Видалити
                edit_btn = tk.Button(self.listFrame, image=self.edit_user_btn_off, borderwidth=0, highlightthickness=0,
                                     bg='#e6e6e6')
                edit_btn.bind("<Enter>", lambda event, h=edit_btn: h.configure(image=self.edit_user_btn_on))
                edit_btn.bind("<Leave>", lambda event, h=edit_btn: h.configure(image=self.edit_user_btn_off))
                edit_btn.grid(row=self.id, column=3, padx=15, sticky='w')
                edit_btn.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: EditUserDialog(parent=self.listFrame, uid=uid, accounts=self.accounts))
                delete_btn = tk.Button(self.listFrame, image=self.delete_btn_off, borderwidth=0,
                                       highlightthickness=0, bg='#e6e6e6')
                delete_btn.bind("<Enter>", lambda event, h=delete_btn: h.configure(image=self.delete_btn_on))
                delete_btn.bind("<Leave>", lambda event, h=delete_btn: h.configure(image=self.delete_btn_off))
                delete_btn.grid(row=self.id, column=4, padx=15, sticky='w')
                delete_btn.bind("<Button-1>", lambda event, uid=str(i[0]), but=but: self.deleteUser(uid=uid))
                tk.Radiobutton(self.listFrame, variable=self.main_page, value=i[0], borderwidth=0, bg='#e6e6e6',
                               highlightthickness=0, command=self.markAsMainPage).grid(row=self.id, column=5, padx=15,
                                                                                       sticky='we')
                self.id = self.id+1
            con.close()
        except Exception as e:
            tkMessageBox.showerror("Error", "{}".format(e.message))
        # Очищаємо поля для ввода
        self.loginField.delete("0", "end")
        self.passwordField.delete("0", "end")


    def markAsMainPage(self):
        # Cпочатку ставимо всім сторінкам False, потім присвоюємо True сторінці яку вибрав юзер
        con = db.connect(database="vkbot")
        cur = con.cursor()
        query = "UPDATE users set main_page=?"
        cur.execute(query, (0,))
        con.commit()
        query2 = "UPDATE users set main_page=? where id=?"
        cur.execute(query2, (1, self.main_page.get()))
        con.commit()
        # Витягуємо юзера щоб потім витягнути з вк дату останнього посту
        user = cur.execute("SELECT login, password From users where id=?;", (self.main_page.get(),)).fetchone()
        con.commit()
        date = vkapi.get_last_post_date(user[0], user[1])
        # Зберігаємо дату останнього посту в конфіг файл
        config = SafeConfigParser()
        config.read('config.ini')
        config.set('post', 'date', str(date))
        config.set('post', 'main_is_group', str(0))
        with open('config.ini', 'w') as f:
            config.write(f)
        con.close()


class EditUserDialog:
    def __init__(self, parent, uid, accounts):
        self.uid = uid
        self.accounts = accounts
        con = db.connect(database="vkbot")
        cur = con.cursor()
        user = cur.execute("SELECT * FROM users WHERE id=?;", (uid,)).fetchone()
        top = self.top = tk.Toplevel(parent)

        tk.Label(top, text="Логин:").grid(row=0)
        tk.Label(top, text="Пароль:").grid(row=1)

        self.e1 = tk.Entry(top)
        self.e2 = tk.Entry(top)
        self.e1.insert(0, user[1])
        self.e2.insert(0, user[2])
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)

        ok = tk.Button(top, text="Сохранить", command=self.ok)
        ok.grid(row=2, column=0)
        cancel = tk.Button(top, text="Отменить", command=self.cancel)
        cancel.grid(row=2, column=1)

    def ok(self):
        con = db.connect(database="vkbot")
        cur = con.cursor()
        vk_id = vkapi.get_vk_id(login=self.e1.get().strip(), password=self.e2.get().strip())
        uname = vk_id[0]['first_name'] + ' ' + vk_id[0]['last_name']
        # This is the qmark style:
        cur.execute("UPDATE users SET login=?, password=?, vk_id=?, name=? WHERE id=?;",
                    (self.e1.get().strip(), self.e2.get().strip(), vk_id[0]['id'], uname, self.uid))
        con.commit()
        con.close()
        Accounts(self.accounts)
        self.top.destroy()

    def cancel(self):
        self.top.destroy()
