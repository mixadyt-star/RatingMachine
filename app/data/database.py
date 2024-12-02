from typing import NoReturn, Literal
import sqlite3

from utils import security

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

def search_for_user(email: str, type: Literal["Child", "Teacher"]) -> tuple:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    if (type == "Child"):
        cursor.execute("SELECT * FROM Children WHERE email = ?", (email,))
    elif (type == "Teacher"):
        cursor.execute("SELECT * FROM Teachers WHERE email = ?", (email,))

    data = cursor.fetchone()

    cursor.close()

    return data

def register(email: str, password: str, full_name: str, type: Literal["Child", "Teacher"]) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    if (type == "Child"):
        cursor.execute("INSERT INTO Children (email, password, full_name) \
                    VALUES (?, ?, ?)", 
                    email, password, full_name)
    elif (type == "Teacher"):
        cursor.execute("INSERT INTO Teachers (email, password, full_name) \
                   VALUES (?, ?, ?)",
                   email, password, full_name)
    
    connection.commit()
    cursor.close()

def check_login(email: str, password: str, type: Literal["Child", "Teacher"]) -> bool:
    user_data = search_for_user(email, type)

    if (user_data):
        loaded_password = user_data[2]
        if (loaded_password == security.hash(password)):
            return True
        
    return False