import sqlite3
import random
class Database(object):
    def __init__(self, name):
        self.conn = sqlite3.connect(name+'.db', timeout=60)
        self.c = self.conn.cursor()
        self.createtables()

    def createtables(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS models(name TEXT,mid INTEGER,createdAt TEXT,"
                        "tokens INTEGER, cs FLOAT, hcs FLOAT, lcs FLOAT, rc INTEGER, alias TEXT, PRIMARY KEY(mid))")

    def insertmodel(self, username, mid, date, tokens, cs):
        self.c.execute("INSERT OR IGNORE INTO models VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (username, mid, date, tokens, cs, cs, cs, 0, username))
        self.conn.commit()

    def getmodel(self, mid):
        t = (mid,)
        self.c.execute('SELECT * FROM models WHERE mid=?', t)
        return self.c.fetchone()

    def getmodelbyname(self, name):
        t = (name,)
        self.c.execute('SELECT * FROM models WHERE name=?', t)
        return self.c.fetchone()

    def updatetokens(self, mid, tokens):
        self.c.execute("SELECT tokens from models WHERE mid=?", (mid,))
        m=self.c.fetchone()[0]
        if m:
            tokens=m+tokens
            self.c.execute("UPDATE models SET tokens = (?) WHERE mid = (?)",
                           (tokens, mid))
            self.conn.commit()

    def updaterc(self, mid, rc):
        self.c.execute("SELECT rc from models WHERE mid=?", (mid,))
        src=self.c.fetchone()[0]
        if src < rc:
            self.c.execute("UPDATE models SET rc = ? WHERE mid = ?",
                           (rc, mid))
            self.conn.commit()

    def updatecs(self, mid, camscore):
        self.c.execute("SELECT cs, hcs, lcs from models WHERE mid=?", (mid,))
        d=self.c.fetchone()
        cs=d[0]
        hcs=d[1]
        lcs=d[2]
        if camscore > hcs:
            self.c.execute("UPDATE models SET cs = ?, hcs = ? WHERE mid = ?",
                           (camscore, camscore, mid))
            self.conn.commit()
        elif camscore < lcs:
            self.c.execute("UPDATE models SET cs = ?, lcs = ? WHERE mid = ?",
                           (camscore, camscore, mid))
            self.conn.commit()
        elif camscore != lcs:
            self.c.execute("UPDATE models SET cs = ? WHERE mid = ?",
                           (camscore, mid))
            self.conn.commit()
