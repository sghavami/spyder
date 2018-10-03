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

try:
    root = "genprogress.org"

    wdb = lite.connect('./gp.db', isolation_level=None)
    rdb = lite.connect('./gp.db', isolation_level=None)
    wdb.execute('pragma journal_mode=wal;')
    rdb.execute('pragma journal_mode=wal;')
    wc = wdb.cursor()
    rc = rdb.cursor()

    while True:
        try:
            dbx(rc, "select url from todo where flag=0 limit 1")
            r = rc.fetchone()
            if r == None:
                open(x, './done.txt').close()
                break;
            l = r[0]
            dbx(wc, 'update todo set flag=1 where url="%s"' %(l))
            log("processing " + l)

            # GET=>read content into page and http code into code=>close http
            conn = urlopen(l)
            page = conn.read()
            code = conn.getcode()
            url = conn.url
            conn.close()

            if url <> l: #if a redir
                dbx(wc, 'insert or ignore into redir values("%s", "%s")' %(l, url)) #record redir
                if urlparse(url).netloc.endswith(root):
                    dbx(wc, 'insert or ignore into todo values("%s", 0)' %(url)) # add dest to todo if not already included
                else:
                    dbx(wc, 'insert or ignore into skip values("%s", 1)' %(url))
                    log("\tNot crawling external link: " + url)
                log("\tForwarding %s to %s" %(l, url))
                continue

            if not urlparse(l).netloc.endswith(root): # record external ref and skip
                dbx(wc, 'insert or ignore into skip values("%s", 1)' %(l))
                log("\tNot crawling external link: " + url)
                continue

            soup = BeautifulSoup(page, "html.parser")
            for hrefs in soup.findAll('a', {'href':True}):
                try:
                    l = urljoin(url, hrefs['href'])
                except UnicodeError:
                    s = hrefs['href'].encode('ascii', 'replace')
                    l = urljoin(url, s)
                if urlparse(l).netloc.endswith(root):
                    dbx(wc, 'insert or ignore into todo values("%s", 0)' %(l)) #add link to todo if not already included
        except Exception, e:
            log("\tError: %s [%s]" %(l, `e`))
            dbx(wc, 'insert or ignore into skip values("%s", 0)' %(l)) #record bad http calls
#end while:
    wdb.close()
    rdb.close()

    log("\nCreepy spider is dead!")
    sys.exit(0) #exit with success
except Exception, e:
    log("Fatal Error: " + `e`)
    sys.exit(1) # exit with error
