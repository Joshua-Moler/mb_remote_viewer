import sqlite3

db_connection = sqlite3.connect('clients.db')
sqlCursor = db_connection.cursor()

try:
    sqlCursor.execute("CREATE TABLE clients(client_key, client_secret)")
except sqlite3.OperationalError:
    pass

try:
    sqlCursor.execute("CREATE TABLE tokens(token_key, token_secret)")
except sqlite3.OperationalError:
    pass

clients = [
    ('___IB_PROTOTYPE_SOFTWARE___', 'S789sdh@^@&*HFdls(S764SDF$'),
    ('___MB_PROTOTYPE_SOFTWARE___', 'H^797&^g(2#$%^ULGG+P:FHTY)')
]
tokens = [
    ('___IB_STATUS_SERVER_ACCESS___', '(*&^545Tyuju9876%^&*(hui*7'),
]

sqlCursor.executemany("INSERT OR IGNORE INTO clients VALUES (?, ?)", clients)
sqlCursor.executemany("INSERT OR IGNORE INTO tokens VALUES (?, ?)", tokens)


sqlCursor.execute(
    "SELECT * from clients")

print(sqlCursor.fetchall())

sqlCursor.execute(
    "SELECT * from tokens")

print(sqlCursor.fetchall())

db_connection.commit()
