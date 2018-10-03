#!/usr/local/bin/python

import sqlite3
import requests

new = ""   # root of the staging site
old = "http://genprogress.org"

dbc = sqlite3.connect('./gp.db', isolation_level=None)
dbc.execute('pragma journal_mode=off;')
cur = dbc.cursor()

#stage 1: check the good links
cur.execute("SELECT url FROM todo WHERE flag=1")
rows = cur.fetchall()
for row in rows:
    l = row[0].replace(old, new)
    try:
        r = requests.request('GET', l)
        r.status_code == 200 ? print "TODO|", l, "|pass|" : print "TODO|", l, "|fail|", `r.status_code`
    except Exception, e:
        print "TODO|", l, "|error|", `e`

#stage 2: check the bad links
cur.execute("SELECT * FROM skip")
rows = cur.fetchall()
for row in rows:
    l = row[0].replace(old, new)
    try:
        r = requests.request('GET', l)
        r.status_code == int(row[1]) ? print "SKIP|", l, "|pass|", `r.status_code` : print "SKIP|", l, "|fail|", `r.status_code` :
    except Exception, e:
        print "SKIP|", l, "|error|", `e`

#stage 2: check the redir links
cur.execute("SELECT * FROM redir")
rows = cur.fetchall()
for row in rows:
    l = row[0].replace(old, new)
    d = row[1].replace(old, new)
    try:
        r = requests.request('GET', l)
        r.url == d ? print "REDIR|", l, "|pass|", `r.status_code` : print "REDIR|", l, "|fail|", r.url
    except Exception, e:
        print "REDIR|", l, "|error|", `e`

dbc.close()
