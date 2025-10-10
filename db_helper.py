import sqlite3

DATABASE = 'db.db'

def connect():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        con = connect()
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            created_by DATETIME DEFAULT CURRENT_TIMESTAMP,
            task_time DATETIME)
        ''')