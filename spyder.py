#!/usr/local/bin/python
#from working dir: nohup python spyder.py >gp.log 2>&1 &
#or: chmod +x spyder.py; nohup spyder.py >gp.log 2>&1 &

import sys
import sqlite3 as lite
from datetime import datetime
from urllib2 import urlopen
from urlparse import urlparse
from urlparse import urljoin
from bs4 import BeautifulSoup

def log(s):
    sys.stderr.write('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) + ": " + s + "\n")
#end log

def dbx(c, s):
    try:
        return c.execute(s)
    except:
        return None
#end exec

log("Itsy bitsy spider is crawling again")
try:
    tot = 0
    redirs = 0
    skips = 0
    root = "genprogress.org"

    dbc = lite.connect('./gp.db')
    c = dbc.cursor()

    dbx(c, "drop table todo")
    dbx(c, "drop table skip")
    dbx(c, "drop table redir")
    dbx(c, "create table todo (url text primary key, flag int)") # flag = done ? T : F
    dbx(c, "create table skip (url text primary key, flag int)") # flag = external ? T : F
    dbx(c, "create table redir (url text primary key, dest text)") # 301 / 302
    dbx(c, "insert into todo values('http://genprogress.org', 0)") # seed
    log("Database is ready and seeded")

    while True:
        try:
            dbc.commit() # help clear inmem cache
            dbx(c, "select url from todo where flag=0 limit 1")
            r = c.fetchone()
            if r == None:
                log("End of the road at depth = " + `tot`)
                break;

            tot += 1
            l = r[0]
            dbx(c, 'update todo set flag=1 where url="%s"' %(l))
            log("processing " + l)

            # GET=>read content into page and http code into code=>close http
            conn = urlopen(l)
            page = conn.read()
            code = conn.getcode()
            url = conn.url
            conn.close()

            if url <> l: #if a redir
                redirs += 1
                dbx(c, 'insert or ignore into redir values("%s", "%s")' %(l, url)) #record redir
                dbx(c, 'insert or ignore into todo values("%s", 0)' %(url)) # add dest to todo if not already included
                log("\tForwarding %s to %s" %(l, url))
                continue

            if not urlparse(l).netloc.endswith(root): # record external ref and skip
                skips += 1
                dbx(c, 'insert or ignore into skip values("%s", 1)' %(l))
                log("\tNot crawling external link: " + url)
                continue

            soup = BeautifulSoup(page, "html.parser")
            for hrefs in soup.findAll('a', {'href':True}):
                try:
                    l = urljoin(url, hrefs['href'])
                except UnicodeError:
                    s = hrefs['href'].encode('ascii', 'replace')
                    l = urljoin(url, s)
                dbx(c, 'insert or ignore into todo values("%s", 0)' %(l)) #add link to todo if not already included
        except Exception, e:
            log("\tError: %s [%s]" %(l, `e`))
            dbx(c, 'insert or ignore into skip values("%s", 0)' %(l)) #record bad http calls
#end while:
    c.close()
    log("\nCreepy spider is dead!")
    sys.exit(0) #exit with success
except Exception, e:
    log("Fatal Error: " + `e`)
    sys.exit(1) # exit with error
