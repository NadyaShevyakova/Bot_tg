import sqlite3
DB_NAME = 'users_id_k.db'
def init_bd():
	connect = sqlite3.connect(DB_NAME)
	cursor = connect.cursor() #id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 0 не нужен тк генерит сам
	cursor.execute("""
		    CREATE TABLE IF NOT EXISTS users_id_k (
		        id INTEGER,
		        k INTEGER,
		        gr INTEGER
		    )""")
	connect.commit()
	connect.close()

def clear():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM users_id_k")
        conn.commit()

def add_k_to_bd(k,id):
    with sqlite3.connect(DB_NAME) as connect:
        # connect.execute(""" INSERT INTO users_id_k (k) VALUES (?) WHERE id = ?""", (k,id))
        connect.execute("""UPDATE users_id_k SET k = ? WHERE id = ?""", (k, id))
        connect.commit()

def add_gr_to_bd(gr,k,id):
    with sqlite3.connect(DB_NAME) as connect: #нужно k тк при смене группы лучше начинать с текущей недели
        connect.execute("""UPDATE users_id_k SET gr = ?, k = ? WHERE id = ?""", (gr,k,id))
        connect.commit()

def add_all_to_bd(id,gr,k):
    with sqlite3.connect(DB_NAME) as connect:
        connect.execute(""" INSERT INTO users_id_k (id,gr,k) VALUES (?, ?, ?)""", (id,gr,k))
        connect.commit()

def get_all_from_bd(id):
    with sqlite3.connect(DB_NAME) as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT k,id,gr FROM users_id_k WHERE id = ?", (id,))
        return cursor.fetchall()