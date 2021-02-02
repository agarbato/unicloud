import sqlite3
from flask import Flask, g

root_dir = "/data"
database = root_dir + "/unicloud.db"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
        #db.row_factory = sqlite3.Row
    return db


def query_db(query, args = (), one = False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

