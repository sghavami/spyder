#!/usr/local/bin/python
#from working dir: nohup python spyder.py >gp.log 2>&1 &
#or: chmod +x spyder.py; nohup spyder.py >gp.log 2>&1 &

import sys
import sqlite3 as lite

try:
    dbc = lite.connect('./gp.db')
    c = dbc.cursor()

    try:
        c.execute("drop table todo")
        c.execute("drop table skip")
        c.execute("drop table redir")
    except:
        pass
    c.execute("create table todo (url text primary key, flag int)") # flag = done ? T : F
    c.execute("create table skip (url text primary key, flag int)") # flag = external ? T : F
    c.execute("create table redir (url text primary key, dest text)") # 301 / 302
    c.execute("insert into todo values('http://genprogress.org', 0)") # seed
    dbc.commit()
    print "Database is ready and seeded"
    exit(0)
except Exception, e:
     print "Fatal Error: %s" %(`e`)
     sys.exit(1) # exit with error
