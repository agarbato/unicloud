import sqlite3
from flask import Flask, g

root_dir = "/data"
database = root_dir + "/unicloud***REMOVED***db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g***REMOVED***_database = sqlite3***REMOVED***connect(database)
        #db***REMOVED***row_factory = sqlite3***REMOVED***Row
    return db

def query_db(query, args = (), one = False):
    cur = get_db()***REMOVED***execute(query, args)
    rv = cur***REMOVED***fetchall()
    cur***REMOVED***close()
    return (rv[0] if rv else None) if one else rv

