import os, json
import random
from random import choice
import sys
import yaml
import time
import inspect
from datetime import datetime
from rethinkdb import r
from app.core import config
from app.db.session import get_rdb

from rethinkdb.errors import RqlRuntimeError, RqlDriverError
# r = RethinkDB()
rdb = r.connect(url=config.RETHINK_DB_URI).repl()


def dec(func):
    def wrapper(*args, **kwargs):
        # print (*args)
        # print(f"ENTERING:\t{func.__name__}")
        result = func(*args, **kwargs)
        # print (f"RESULT:\t\t{func.__name__} = {result}")
        # print(f"EXITING:\t{func.__name__}")
        return result
    return wrapper

def create_table (t, g):
    try:
        if t not in r.db(config.RDB_DB).table_list().run(rdb):
            c = r.db(config.RDB_DB).table_create(t).run(rdb)
        else:
            print (f"table {t} exists")
    except Exception as e:
        print (f"{inspect.stack()[0][3]} - {str(e)}")
    # print ()

# write_data(rdb, config.LOGS, {'name': result[3], 'user': c, result: error_state})

def write_data (g, t, d):
    try:
        tb = r.db(config.RDB_DB).table(t)
        if 'start' in d:
            d['start'] = r.now()
        if 'end' in d:
            d['end'] = None
        d['created_at'] = r.now()
        _r = tb.insert(d).run(rdb)
        print (f"RESULT: {inspect.stack()[0][3]} - {_r} {locals()}")
        print (f"run_id: {d['run_id']}")
    except Exception as e:
        print (f"{inspect.stack()[0][3]} - {str(e)} {locals()}")
        raise ValueError (f"{inspect.stack()[0][3]} - {str(e)}")

# r.table("posts").filter(
#     r.hashMap("author", "William")).update(r.hashMap("status", "published")
# ).run(conn);
def update_data (g, t, d, f):
    try:
        if 'end' in d:
            d['end'] = r.now()

        tb = r.db(config.RDB_DB).table(t)
        _u = tb.filter(f).update(d).run(rdb)
        print (f"RESULT: {inspect.stack()[0][3]} - {_u} {locals()}")
        # print (f"run_id: {d['run_id']}")
    except Exception as e:
        print (f"{inspect.stack()[0][3]} - {str(e)} {locals()}")
        raise ValueError (f"{inspect.stack()[0][3]} - {str(e)}")

@dec
def get_data (t, f):
    try:
        d = []
        tb = r.db(config.RDB_DB).table(t)
        if f:
            d = tb.filter(f).run(rdb)
        else:
            d = tb.run(rdb)
        result = []
        for _d in d:
            result.append(_d)
        return result
    except Exception as e:
        print (f"{inspect.stack()[0][3]} - {str(e)} {locals()}")
        raise ValueError (f"{inspect.stack()[0][3]} - {str(e)}")




def get_random_bool ():
    return True
    # return random.choice([True, True])

def r_date():
    timezone = time.strftime("%z")
    reql_tz = r.make_timezone(timezone[:3] + ":" + timezone[3:])
    return datetime.now()    