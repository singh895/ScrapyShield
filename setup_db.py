import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('test.db')
c = conn.cursor()

# Create the users table
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

# Insert some sample data
c.executemany('''
    INSERT INTO users (username, password) VALUES (?, ?)
''', [
    ('purva', 'password3'),
    ('saanvi', 'password1'),
    ('sean', 'password2')
])

# Commit and close connection
conn.commit()
conn.close()

print("Database setup complete!")