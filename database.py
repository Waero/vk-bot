#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as db


c = db.connect(database="vkbot")
cu = c.cursor()
try:
    cu.execute("""
         CREATE TABLE users (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
          login VARCHAR,
          password VARCHAR,
          friends INTEGER
         );
""")
except db.DatabaseError, x:
    print "DB Error: ", x
c.commit()
c.close()
