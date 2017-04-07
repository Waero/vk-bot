# -*- coding: utf-8 -*-
import Tkinter as tk
import os
import tkFileDialog
from PIL import Image, ImageTk
from ConfigParser import SafeConfigParser
import tkFont
from ttk import Combobox
import sqlite3 as db
import time

# Поля юзера в Settings
import vkapi
from vkapi import get_group_id


class FabySettings:

    def __init__(self, Sbody):
        self.edit_btn_off = ImageTk.PhotoImage(Image.open("img/edit_btn_off.png"))
        self.edit_btn_on = ImageTk.PhotoImage(Image.open("img/edit_btn_on.png"))
        self.save_btn_off = ImageTk.PhotoImage(Image.open("img/save_btn_off.png"))
        self.save_btn_on = ImageTk.PhotoImage(Image.open("img/save_btn_on.png"))
        self.edit_status = 0
        self.edit_message = 0
        self.edit__mutal_status = 0
        self.edit_max_friend_status = 0
        self.edit_group_status = 0
        fontForLabels = tkFont.Font(family='Helvetica', size=10)

# Виводимо час для рандому
        tk.Label(Sbody, text='Время задержки в секундах', bg='#e6e6e6', font=fontForLabels).grid(row=0, column=3, columnspan=3, pady=5)
        tk.Label(Sbody, text=' от : ', bg='#e6e6e6').grid(row=1, column=2)
        self.min_time = tk.Entry(Sbody, width=10)
        self.min_time.grid(row=1, column=3)
        tk.Label(Sbody, text=' до : ', bg='#e6e6e6').grid(row=1, column=4)
        self.max_time = tk.Entry(Sbody, width=10)
        self.max_time.grid(row=1, column=5)

        # Кнопка Редактировать
        self.edit_time_btn = tk.Button(Sbody,
                                      #highlightbackground='#e6e6e6',
                                      #highlightcolor='#e6e6e6',
                                      #activebackground='#e6e6e6',
                                      bg='#e6e6e6',
                                      borderwidth=0,
                                      highlightthickness=0,
                                      image=self.edit_btn_off
                                      )
        self.edit_time_btn.bind("<Enter>", lambda event, h=self.edit_time_btn: h.configure(bg='#e6e6e6', image=self.edit_btn_on))
        self.edit_time_btn.bind("<Leave>", lambda event, h=self.edit_time_btn: h.configure(bg='#e6e6e6', image=self.edit_btn_off))
        self.edit_time_btn.bind("<Button-1>", self.edit_time)
        self.edit_time_btn.grid(row=0, rowspan=2, column=7, padx=15)

        # Кнопка Сохранить
        self.save_time_btn = tk.Button(Sbody,
                                      #highlightbackground='#e6e6e6',
                                      #highlightcolor='#e6e6e6',
                                      #activebackground='#e6e6e6',
                                      bg='#e6e6e6',
                                      borderwidth=0,
                                      highlightthickness=0,
                                      image=self.save_btn_off
                                      )
        self.save_time_btn.bind("<Enter>", lambda event, h=self.save_time_btn: h.configure(bg='#e6e6e6', image=self.save_btn_on))
        self.save_time_btn.bind("<Leave>", lambda event, h=self.save_time_btn: h.configure(bg='#e6e6e6', image=self.save_btn_off))
        self.save_time_btn.bind("<Button-1>", self.edit_time)


        # Заповнюємо min і max значеннями з конфіг файла
        config = SafeConfigParser()
        config.read('config.ini')
        max = config.get('main', 'max')
        min = config.get('main', 'min')
        mutal = config.get('main', 'mutal')
        message = config.get('main', 'message')
        friend_sex = config.getint('main', 'friend_sex')
        auto_answer = config.getint('main', 'auto_answer')
        auto_post = config.getint('main', 'auto_post')
        max_friends = config.getint('main', 'max_friends')
        self.main_group_link = config.get('post', 'main_group_link')
        self.invite_in_group_link = config.get('group', 'invite_in_group_link')
        self.suggested_friends = config.getint('main', 'suggested_type')

        self.min_time.insert(0, min)
        self.max_time.insert(0, max)
        self.min_time.config(state='disabled')
        self.max_time.config(state='disabled')

# Настройка минимального количества общих друзей
        tk.Label(Sbody, text=' Минимальное количество общих друзей ', bg='#e6e6e6').grid(row=2, column=2, columnspan=5, pady=5)
        self.mutal_entry = tk.Entry(Sbody,width=10)
        self.mutal_entry.grid(row=3, column=0, columnspan=7)
        self.mutal_entry.insert(0, mutal)
        self.mutal_entry.config(state='disabled')

# Кнопка Редактировать количествo общих друзей
        self.edit_mutalf_btn = tk.Button(Sbody,
                                      #highlightbackground='#e6e6e6',
                                      #highlightcolor='#e6e6e6',
                                      #activebackground='#e6e6e6',
                                      bg='#e6e6e6',
                                      borderwidth=0,
                                      highlightthickness=0,
                                      image=self.edit_btn_off
                                      )
        self.edit_mutalf_btn.bind("<Enter>", lambda event, h=self.edit_mutalf_btn: h.configure(bg='#e6e6e6', image=self.edit_btn_on))
        self.edit_mutalf_btn.bind("<Leave>", lambda event, h=self.edit_mutalf_btn: h.configure(bg='#e6e6e6', image=self.edit_btn_off))
        self.edit_mutalf_btn.bind("<Button-1>", self.edit_mutal)
        self.edit_mutalf_btn.grid(row=2, rowspan=3, column=7, padx=15)

        # Кнопка Сохранить количествo общих друзей
        self.save_mutalf_btn = tk.Button(Sbody,
                                      #highlightbackground='#e6e6e6',
                                      #highlightcolor='#e6e6e6',
                                      #activebackground='#e6e6e6',
                                      bg='#e6e6e6',
                                      borderwidth=0,
                                      highlightthickness=0,
                                      image=self.save_btn_off
                                      )
        self.save_mutalf_btn.bind("<Enter>", lambda event, h=self.save_mutalf_btn: h.configure(bg='#e6e6e6', image=self.save_btn_on))
        self.save_mutalf_btn.bind("<Leave>", lambda event, h=self.save_mutalf_btn: h.configure(bg='#e6e6e6', image=self.save_btn_off))
        self.save_mutalf_btn.bind("<Button-1>", self.edit_mutal)

# Максимальна к-сть друзів
        tk.Label(Sbody, text=' Максимальное количество друзей ', bg='#e6e6e6').grid(row=5, column=2, columnspan=5,
                                                                                         pady=5)
        self.max_friend_entry = tk.Entry(Sbody, width=10)
        self.max_friend_entry.grid(row=6, column=0, columnspan=7)
        self.max_friend_entry.insert(0, max_friends)
        self.max_friend_entry.config(state='disabled')

        # Кнопка Редактировать максимальну к-сть друзів
        self.edit_max_friend_btn = tk.Button(Sbody,
                                         # highlightbackground='#e6e6e6',
                                         # highlightcolor='#e6e6e6',
                                         # activebackground='#e6e6e6',
                                         bg='#e6e6e6',
                                         borderwidth=0,
                                         highlightthickness=0,
                                         image=self.edit_btn_off
                                         )
        self.edit_max_friend_btn.bind("<Enter>", lambda event, h=self.edit_max_friend_btn: h.configure(bg='#e6e6e6',
                                                                                               image=self.edit_btn_on))
        self.edit_max_friend_btn.bind("<Leave>", lambda event, h=self.edit_max_friend_btn: h.configure(bg='#e6e6e6',
                                                                                               image=self.edit_btn_off))
        self.edit_max_friend_btn.bind("<Button-1>", self.edit_max_friend)
        self.edit_max_friend_btn.grid(row=5, rowspan=3, column=7, padx=15)

        # Кнопка Сохранить максимальну к-сть друзів
        self.save_max_friend_btn = tk.Button(Sbody,
                                         # highlightbackground='#e6e6e6',
                                         # highlightcolor='#e6e6e6',
                                         # activebackground='#e6e6e6',
                                         bg='#e6e6e6',
                                         borderwidth=0,
                                         highlightthickness=0,
                                         image=self.save_btn_off
                                         )
        self.save_max_friend_btn.bind("<Enter>", lambda event, h=self.save_max_friend_btn: h.configure(bg='#e6e6e6',
                                                                                               image=self.save_btn_on))
        self.save_max_friend_btn.bind("<Leave>", lambda event, h=self.save_max_friend_btn: h.configure(bg='#e6e6e6',
                                                                                               image=self.save_btn_off))
        self.save_max_friend_btn.bind("<Button-1>", self.edit_max_friend)

# Для налаштувань статі
        tk.Label(Sbody, text=' Добавлять только ', bg='#e6e6e6').grid(row=8, column=1, columnspan=3,
                                                                                    pady=7)

        self.combobox = Combobox(Sbody, values=["Всех", "Женщин", "Мужчин"])
        code = {1: 1, 2: 2, 3: 0}
        self.combobox.current(code[friend_sex])
        self.combobox.configure(state='readonly')
        self.combobox.bind("<<ComboboxSelected>>", self.combo)
        self.combobox.grid(row=8, column=4, columnspan=2)


        tk.Label(Sbody, text=' Сделать главной групу ', bg='#e6e6e6').grid(row=9, column=1, columnspan=3, pady=6)
        self.group_make_main = tk.Entry(Sbody, width=20)
        self.group_make_main.grid(row=9, column=1, columnspan=7)
        tk.Label(Sbody, text=' Приглашать в групу ', bg='#e6e6e6').grid(row=10, column=1, columnspan=3, pady=4)
        self.group_invite = tk.Entry(Sbody, width=20)
        self.group_invite.grid(row=10, column=1, columnspan=7)
        self.group_make_main.insert(0, self.main_group_link)
        self.group_invite.insert(0, self.invite_in_group_link)
        self.group_make_main.config(state='disabled')
        self.group_invite.config(state='disabled')

        # Кнопка Редактировать настройки груп
        self.edit_group_btn = tk.Button(Sbody,
                                         bg='#e6e6e6',
                                         borderwidth=0,
                                         highlightthickness=0,
                                         image=self.edit_btn_off
                                         )
        self.edit_group_btn.bind("<Enter>", lambda event, h=self.edit_group_btn: h.configure(bg='#e6e6e6',
                                                                                               image=self.edit_btn_on))
        self.edit_group_btn.bind("<Leave>", lambda event, h=self.edit_group_btn: h.configure(bg='#e6e6e6',
                                                                                               image=self.edit_btn_off))
        self.edit_group_btn.bind("<Button-1>", self.edit_group)
        self.edit_group_btn.grid(row=9, rowspan=2, column=7, padx=15)

        # Кнопка Сохранить настройки груп
        self.save_group_btn = tk.Button(Sbody,
                                         bg='#e6e6e6',
                                         borderwidth=0,
                                         highlightthickness=0,
                                         image=self.save_btn_off
                                         )
        self.save_group_btn.bind("<Enter>", lambda event, h=self.save_group_btn: h.configure(bg='#e6e6e6',
                                                                                               image=self.save_btn_on))
        self.save_group_btn.bind("<Leave>", lambda event, h=self.save_group_btn: h.configure(bg='#e6e6e6',
                                                                                               image=self.save_btn_off))
        self.save_group_btn.bind("<Button-1>", self.edit_group)

# Чекбокс для вибору типу додавання друзів
        self.sug_friends = tk.IntVar()
        cf = tk.Checkbutton(
            Sbody, text="Добавлять друзей через Возможные друзья",
            variable=self.sug_friends,
            bg='#e6e6e6',
            highlightthickness=0,
            command=self.change_suggested_type)
        cf.grid(row=11, columnspan=10, padx=10, pady=7, sticky='w')
        if self.suggested_friends == 1:
            cf.select()

# Чекбокс для авто-ответа
        self.var = tk.IntVar()
        c = tk.Checkbutton(
            Sbody, text="Авто-ответ",
            variable=self.var,
            bg='#e6e6e6',
            highlightthickness=0,
            command=self.change_auto_answer)
        c.grid(row=13, columnspan=4, padx=10, sticky='w')
        if auto_answer == 1:
            c.select()

# Чекбокс для авто-посту
        self.a_post = tk.IntVar()
        ch = tk.Checkbutton(
            Sbody, text="Авто-пост",
            variable=self.a_post,
            bg='#e6e6e6',
            highlightthickness=0,
            command=self.change_auto_post)
        ch.grid(row=13, column=5, columnspan=4, padx=10, sticky='w')
        if auto_post == 1:
            ch.select()

# Текстове поле для авто-ответа
        tk.Label(Sbody, text='Настройка авто-ответа', bg='#e6e6e6').grid(row=12, columnspan=7, pady=2)
        self.automessage = tk.Text(Sbody, width=40, height=5, bg='#e6e6e6', wrap='word', foreground='#858585')
        self.automessage.grid(row=14, rowspan=5, columnspan=7, padx=10)
        self.automessage.insert(1.0, message)
        self.automessage.config(state='disabled')

# Кнопка Редактировать для Авто-ответа
        self.edit_message_btn = tk.Button(Sbody,
                                      #highlightbackground='#e6e6e6',
                                      #highlightcolor='#e6e6e6',
                                      #activebackground='#e6e6e6',
                                      bg='#e6e6e6',
                                      borderwidth=0,
                                      highlightthickness=0,
                                      image=self.edit_btn_off
                                      )
        self.edit_message_btn.bind("<Enter>", lambda event, h=self.edit_message_btn: h.configure(bg='#e6e6e6', image=self.edit_btn_on))
        self.edit_message_btn.bind("<Leave>", lambda event, h=self.edit_message_btn: h.configure(bg='#e6e6e6', image=self.edit_btn_off))
        self.edit_message_btn.bind("<Button-1>", self.editMessage)
        self.edit_message_btn.grid(row=11, rowspan=6, column=7)

    # Кнопка Сохранить для Автоответа
        self.save_message_btn = tk.Button(Sbody,
                                   # highlightbackground='#e6e6e6',
                                   # highlightcolor='#e6e6e6',
                                   # activebackground='#e6e6e6',
                                   bg='#e6e6e6',
                                   borderwidth=0,
                                   highlightthickness=0,
                                   image=self.save_btn_off
                                   )
        self.save_message_btn.bind("<Enter>", lambda event, h=self.save_message_btn: h.configure(bg='#e6e6e6', image=self.save_btn_on))
        self.save_message_btn.bind("<Leave>", lambda event, h=self.save_message_btn: h.configure(bg='#e6e6e6', image=self.save_btn_off))
        self.save_message_btn.bind("<Button-1>", self.editMessage)
        self.Sbody = Sbody  # Для напису "Найдено {} фото
        self.upload_photo = tk.Button(Sbody, text='Вибирите папку с фото', command=self.askdirectory).grid(row=13, rowspan=6, column=7)

        self.dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = False
        options['parent'] = Sbody
        options['title'] = 'This is a title'

    def askdirectory(self):
        """Returns a selected directoryname."""
        z = tkFileDialog.askdirectory(**self.dir_opt)

        # Зберігаємо в конфіг значення
        config = SafeConfigParser()
        config.read('config.ini')
        config.set('photo', 'upload_dir', z.encode('utf-8'))
        config.set('photo', 'upload_photo', str(1))

        with open('config.ini', 'w') as f:
            config.write(f)
        files = [f for f in os.listdir(z) if os.path.isfile(os.path.join(z, f))]
        if 'Thumbs.db' in files: files.remove('Thumbs.db')  # Тимчасове рішення, треба зробити перевірку щоб додавати тільки фото
        tk.Label(self.Sbody, text='Будет загружено {} фото'.format(len(files)), bg='#e6e6e6', fg='#757575').grid(row=16, rowspan=6, column=7)

        # Метод для кнопок Edit i Save максимальної к-сті друзів
    def edit_max_friend(self, event):
        if self.edit_max_friend_status == 0:
            self.max_friend_entry.config(state='normal')
            self.edit_max_friend_status = 1
            self.edit_max_friend_btn.grid_forget()
            self.save_max_friend_btn.grid(row=5, rowspan=3, column=7, padx=15)
        else:
            self.max_friend_entry.config(state='disabled')
            self.edit_max_friend_status = 0
            self.save_max_friend_btn.grid_forget()
            self.edit_max_friend_btn.grid(row=5, rowspan=3, column=7, padx=15)
                # Зберігаємо в конфіг значення максимальної к-сті друзів
            config = SafeConfigParser()
            config.read('config.ini')
            config.set('main', 'max_friends', self.max_friend_entry.get())

            with open('config.ini', 'w') as f:
                config.write(f)

    # Метод для кнопок Edit i Save спільних друзів
    def edit_mutal(self, event):
        if self.edit__mutal_status == 0:
            self.mutal_entry.config(state='normal')
            self.edit__mutal_status = 1
            self.edit_mutalf_btn.grid_forget()
            self.save_mutalf_btn.grid(row=2, rowspan=3, column=7, padx=15)
        else:
            self.mutal_entry.config(state='disabled')
            self.edit__mutal_status = 0
            self.save_mutalf_btn.grid_forget()
            self.edit_mutalf_btn.grid(row=2, rowspan=3, column=7, padx=15)
                # Зберігаємо в конфіг значення mutal
            config = SafeConfigParser()
            config.read('config.ini')
            config.set('main', 'mutal', self.mutal_entry.get())

            with open('config.ini', 'w') as f:
                config.write(f)

    # Метод для зміни пола
    def combo(self, event):
        config = SafeConfigParser()
        config.read('config.ini')
        code = {u'Женщин': 1, u'Мужчин': 2, u'Всех': 3}
        config.set('main', 'friend_sex', str(code[self.combobox.get()]))
        with open('config.ini', 'w') as f:
            config.write(f)

    # Метод для вибору типу додавання в друзі
    def change_suggested_type(self):
        # Зберігаємо в конфіг значення
        config = SafeConfigParser()
        config.read('config.ini')
        config.set('main', 'suggested_type', str(self.sug_friends.get()))
        with open('config.ini', 'w') as f:
            config.write(f)

    # Метод для чекбокса авто-ответа
    def change_auto_answer(self):
        # Зберігаємо в конфіг значення
        config = SafeConfigParser()
        config.read('config.ini')
        config.set('main', 'auto_answer', str(self.var.get()))
        config.set('photo', 'auto_answer_on_comments', str(int(time.time())))
        with open('config.ini', 'w') as f:
            config.write(f)

        # Метод для чекбокса авто-посту
    def change_auto_post(self):
             # Зберігаємо в конфіг значення
            config = SafeConfigParser()
            config.read('config.ini')
            config.set('main', 'auto_post', str(self.a_post.get()))
            with open('config.ini', 'w') as f:
                    config.write(f)

    # Метод для кнопки Edit і Save для рандомного часу
    def edit_time(self, event):
        if self.edit_status == 0:
            self.min_time.config(state='normal')
            self.max_time.config(state='normal')
            self.edit_status = 1
            self.edit_time_btn.grid_forget()
            self.save_time_btn.grid(row=0, rowspan=2, column=7, padx=15)
        else:
            self.min_time.config(state='disabled')
            self.max_time.config(state='disabled')
            self.edit_status = 0
            self.save_time_btn.grid_forget()
            self.edit_time_btn.grid(row=0, rowspan=2, column=7, padx=15)
                # Зберігаємо в конфіг значення max i min
            config = SafeConfigParser()
            config.read('config.ini')
                # config.add_section('main')
            config.set('main', 'max', self.max_time.get())
            config.set('main', 'min', self.min_time.get())

            with open('config.ini', 'w') as f:
                config.write(f)

# Метод для редагування тексту для автоответа
    def editMessage(self, event):
            if self.edit_message == 0:
                    self.automessage.config(state='normal', bg='#F8F8FF', foreground='black')
                    self.edit_message = 1

                    self.edit_message_btn.grid_forget()
                    self.save_message_btn.grid(row=11, rowspan=6, column=7)
            else:
                    self.automessage.config(state='disabled', bg='#e6e6e6', foreground='#858585')
                    self.edit_message = 0
                    self.save_message_btn.grid_forget()
                    self.edit_message_btn.grid(row=11, rowspan=6, column=7)
                    # Зберігаємо в конфіг значення max i min
                    config = SafeConfigParser()
                    config.read('config.ini')
                    # config.add_section('main')
                    config.set('main', 'message', self.automessage.get(1.0, 'end').encode('utf8'))

                    with open('config.ini', 'w') as f:
                        config.write(f)

    # Метод щоб оновлювати групи (групу як головну сторінку, та групу в яку будемо запрошувати людей)
    def edit_group(self, event):
        if self.edit_group_status == 0:
            self.group_make_main.config(state='normal')
            self.group_invite.config(state='normal')
            self.edit_group_status = 1
            self.edit_group_btn.grid_forget()
            self.save_group_btn.grid(row=9, rowspan=2, column=7, padx=15)
        else:
            self.group_make_main.config(state='disabled')
            self.group_invite.config(state='disabled')
            self.edit_group_status = 0
            self.save_group_btn.grid_forget()
            self.edit_group_btn.grid(row=9, rowspan=2, column=7, padx=15)
                # Зберігаємо в конфіг значення але спочатку перевіряємо
            config = SafeConfigParser()
            config.read('config.ini')
            # Перевірка чи є встановлена група як головна сторінка
            id_m = self.group_make_main.get()
            if id_m != '':
                if self.main_group_link == id_m: # Щоб не оновлювати якщо не було змін
                    pass
                else:
                    group_name = id_m.rsplit('/')
                    group_id = get_group_id(group_name[-1])
                    config.set('post', 'main_is_group', str(group_id))
                    # Cтавимо всім сторінкам False як головних сторінок, бо головна зараз група!
                    con = db.connect(database="vkbot")
                    cur = con.cursor()
                    query = "UPDATE users set main_page=?"
                    cur.execute(query, (0,))
                    con.commit()
                    con.close()
                    date = vkapi.get_last_post_date_group('-' + str(group_id))
                    # Зберігаємо дату останнього посту в конфіг файл
                    config.set('post', 'date', str(date))
                    config.set('post', 'main_group_link', str(id_m))
            else:
                config.set('post', 'main_is_group', str(0))
                config.set('post', 'main_group_link', str(''))

            # Перевірка чи є заповнена група в яку будемо запрошувати
            id_i = self.group_invite.get()
            if id_i != '':
                if self.invite_in_group_link == id_i: # Щоб не оновлювати якщо не було змін
                    pass
                else:
                    group_name_i = id_i.rsplit('/')
                    group_i_id = get_group_id(group_name_i[-1])
                    config.set('group', 'invite_in_group', str(group_i_id))
                    config.set('group', 'invite_in_group_link', str(id_i))
            else:
                config.set('group', 'invite_in_group', str(0))
                config.set('group', 'invite_in_group_link', str(''))

            with open('config.ini', 'w') as f:
                config.write(f)