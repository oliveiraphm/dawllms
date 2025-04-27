import sqlite3

conn = sqlite3.connect('data/my_test_database.db')

cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER
    )
''')

cur.execute('INSERT INTO users (name, age) VALUES (?, ?)', ('Alice', 30))

conn.commit()

cur.execute('SELECT * FROM users')
rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()