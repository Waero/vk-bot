# -*- coding: utf-8 -*-
import Tkinter as tk
from PIL import Image, ImageTk
from ConfigParser import SafeConfigParser
from ttk import Combobox

# Поля юзера в Settings



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

# Виводимо час для рандому
        tk.Label(Sbody, text='Время задержки в секундах', bg='#e6e6e6').grid(row=0, column=3, columnspan=3, pady=8)
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
        max_friends = config.getint('main', 'max_friends')

        self.min_time.insert(0, min)
        self.max_time.insert(0, max)
        self.min_time.config(state='disabled')
        self.max_time.config(state='disabled')

# Настройка минимального количества общих друзей
        tk.Label(Sbody, text=' Минимальное количество общих друзей ', bg='#e6e6e6').grid(row=2, column=2, columnspan=5, pady=10)
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
                                                                                         pady=10)
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
                                                                                    pady=15)

        #all= tk.Radiobutton(Sbody, text="Всех", variable=varik, value=3, bg='#e6e6e6',highlightthickness=0)
        #all.grid(row=9, column=1, columnspan=2)
        #women = tk.Radiobutton(Sbody, text="Женщин", variable=varik, value=1, bg='#e6e6e6',highlightthickness=0)
        #women.grid(row=9, column=3, columnspan=2, pady=10)
        #man = tk.Radiobutton(Sbody, text="Мужчин", variable=varik, value=2, bg='#e6e6e6',highlightthickness=0)
        #man.grid(row=9, column=5, columnspan=2 ,pady=10)
        #all.invoke()

        self.combobox = Combobox(Sbody, values=["Всех", "Женщин", "Мужчин"])
        code = {1: 1, 2: 2, 3: 0}
        self.combobox.current(code[friend_sex])
        self.combobox.configure(state='readonly')
        self.combobox.bind("<<ComboboxSelected>>", self.combo)
        self.combobox.grid(row=8, column=4, columnspan=2)

# Чекбокс для авто-ответа
        self.var = tk.IntVar()
        c = tk.Checkbutton(
            Sbody, text="Авто-ответ",
            variable=self.var,
            bg='#e6e6e6',
            highlightthickness=0,
            command=self.change_auto_answer)
        c.grid(row=11, columnspan=4, padx=10, sticky='w')
        if auto_answer == 1:
            c.select()

# Текстове поле для авто-ответа
        tk.Label(Sbody, text='Настройка авто-ответа', bg='#e6e6e6').grid(row=10, columnspan=7, pady=10)
        self.automessage = tk.Text(Sbody, width=40, height=7, bg='#e6e6e6', wrap='word', foreground='#858585')
        self.automessage.grid(row=12, rowspan=5, columnspan=7, padx=10)
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
        self.edit_message_btn.grid(row=10, rowspan=6, column=7)

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


    # Метод для чекбокса авто-ответа
    def change_auto_answer(self):
        # Зберігаємо в конфіг значення
        config = SafeConfigParser()
        config.read('config.ini')
        config.set('main', 'auto_answer', str(self.var.get()))
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
                    self.save_message_btn.grid(row=10, rowspan=6, column=7)
            else:
                    self.automessage.config(state='disabled', bg='#e6e6e6', foreground='#858585')
                    self.edit_message = 0
                    self.save_message_btn.grid_forget()
                    self.edit_message_btn.grid(row=10, rowspan=6, column=7)
                    # Зберігаємо в конфіг значення max i min
                    config = SafeConfigParser()
                    config.read('config.ini')
                    # config.add_section('main')
                    config.set('main', 'message', self.automessage.get(1.0, 'end').encode('utf8'))

                    with open('config.ini', 'w') as f:
                        config.write(f)
