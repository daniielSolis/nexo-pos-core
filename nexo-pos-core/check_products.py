import sqlite3
conn = sqlite3.connect("nexo.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM productos")
print(cursor.fetchall())
conn.close()