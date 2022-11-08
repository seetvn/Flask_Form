
import sqlite3
con = sqlite3.connect('test.db')
cur = con.cursor()
for users in cur.execute("SELECT first_name,last_name,email FROM User"):
    print(users)