from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from rethinkdb import r
import os

from app.core import config

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_rdb():
    rdb = r.connect(url=config.RETHINK_DB_URI).repl()
    try:

        if config.RDB_DB not in r.db_list().run(rdb):
            d = r.db_create(config.RDB_DB).run(rdb)
        else:
            print (f"database {config.RDB_DB} exists")

    except Exception as e:
        print (str(e))

    try:
        yield rdb
    finally:
        rdb.close()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
