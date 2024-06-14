import sqlite3


BOT_TOKEN = "7487431286:AAHbG_AbyjeazGvErOwH99Z6EjKLS14r7uY"

conn = sqlite3.connect('userdata.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY, 
        first_name TEXT, 
        last_name TEXT,
        age INTEGER,
        address TEXT,
        proficiency TEXT,
        phone_number TEXT
    )
''')
conn.commit()
