import sqlite3

conn = sqlite3.connect('data/games.db')

cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rank INT, 
        name TEXT,
        platform TEXT,
        year INT,
        genre TEXT,
        publisher TEXT, 
        americasales NUMERIC,
        eusales NUMERIC,
        japansales NUMERIC,
        othersales NUMERIC,
        globalsales NUMERIC
    );
''')

conn.commit()

cur.execute('SELECT COUNT(*) FROM games')
rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()