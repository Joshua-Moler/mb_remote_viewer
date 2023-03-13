import os

PROJECT_NAME = "maybell-v1.0"

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
RETHINK_DB_URI=os.getenv('RETHINK_URL')
RDB_DB=os.getenv('RDB_DB')

API_V1_STR = "/api/v1"

LOGS = 'logs'
EVENTS = 'events'
STATUS = 'status'
USERS = 'users'
