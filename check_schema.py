import sqlite3

conn = sqlite3.connect('AITradeGame.db')
cursor = conn.cursor()

# Get table schema
cursor.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="coins"')
result = cursor.fetchone()
if result:
    print("Coins table schema:")
    print(result[0])
else:
    print("Coins table not found")

conn.close()
