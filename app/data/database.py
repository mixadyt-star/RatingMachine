from typing import NoReturn, List
import sqlite3

from utils import security

connection = sqlite3.connect("main.db")
cursor = connection.cursor()

# Create table Children
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS Children (
id INTEGER PRIMARY KEY AUTOINCREMENT,
full_name VARCHAR(255) NOT NULL,
form VARCHAR(255) NOT NULL,
marks TEXT NOT NULL
)
"""
)

# Create table Teachers
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS Teachers (
id INTEGER PRIMARY KEY AUTOINCREMENT,
email VARCHAR(255) NOT NULL,
password VARCHAR(255) NOT NULL,
full_name VARCHAR(255),
subject VARCHAR(255)
)
"""
)

connection.commit()
cursor.close()
connection.close()

def get_children(form: str) -> List[tuple]:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Children \
                    WHERE form = ? \
                    ORDER BY full_name ASC", (form,))
    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data

def search_for_teacher(email: str) -> tuple:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Teachers WHERE email = ?", (email,))
    data = cursor.fetchone()

    cursor.close()
    connection.close()

    return data

def delete_child(id: int):
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Children \
                   WHERE id = ?", (id,))
    
    connection.commit()
    cursor.close()
    connection.close()

def check_child(id: int) -> bool:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Children \
                    WHERE id = ?", (id,))
    alive = bool(cursor.fetchone())

    cursor.close()
    connection.close()

    return alive

def register_child(full_name: str, form: str) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Children (full_name, form, marks) \
                    VALUES (?, ?, ?)",
                    (full_name, form, "{}"))
    
    connection.commit()
    cursor.close()
    connection.close()

def register_teacher(email: str, password: str) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Teachers (email, password) \
                    VALUES (?, ?)",
                    (email, password))
    
    connection.commit()
    cursor.close()
    connection.close()

def check_login(email: str, password: str) -> bool:
    user_data = search_for_teacher(email)

    if (user_data):
        loaded_password = user_data[2]
        if (loaded_password == security.hash(password)):
            return True
        
    return False