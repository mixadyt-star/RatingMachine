from typing import NoReturn
import sqlite3

connection = sqlite3.connect("main.db")
cursor = connection.cursor()

# Create table Children
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS Children (
id INT PRIMARY KEY,
email VARCHAR(255) NOT NULL,
password VARCHAR(255) NOT NULL,
full_name VARCHAR(255) NOT NULL,
form VARCHAR(255)
)
"""
)

# Create table Teachers
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS Teachers (
id INT PRIMARY KEY,
email VARCHAR(255) NOT NULL,
password VARCHAR(255) NOT NULL,
full_name VARCHAR(255) NOT NULL,
subject VARCHAR(255),
children TEXT
)
"""
)

connection.commit()
cursor.close()

def search_for_child(email: str) -> tuple:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Children WHERE email = ?", (email,))
    child_data = cursor.fetchone()

    cursor.close()

    return child_data

def search_for_teacher(email: str) -> tuple:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Teachers WHERE email = ?", (email,))
    child_data = cursor.fetchone()

    cursor.close()

    return child_data

def register_child(email: str, password: str, full_name: str) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Children (email, password, full_name) \
                   VALUES (?, ?, ?)", 
                   email, password, full_name)
    
    connection.commit()
    cursor.close()

def register_teacher(email: str, password: str, full_name: str) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Teachers (email, password, full_name) \
                   VALUES (?, ?, ?)",
                   email, password, full_name)
    
    connection.commit()
    cursor.close()