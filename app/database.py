from typing import NoReturn
import sqlite3

connection = sqlite3.connect("main.db")
cursor = connection.cursor()

# Create table Children
cursor.execute(
"""
CREATE TABLE Children IF NOT EXISTS (
id INT NOT NULL AUTO_INCREMENT,
email TEXT NOT NULL,
password TEXT NOT NULL,
full_name TEXT NOT NULL,
form TEXT
)
"""
)

# Create table Teachers
cursor.execute(
"""
CREATE TABLE Teachers IF NOT EXISTS (
id INT NOT NULL AUTO_INCREMENT,
email TEXT NOT NULL,
password TEXT NOT NULL,
full_name TEXT NOT NULL,
subject TEXT,
children TEXT
)
"""
)

connection.commit()
cursor.close()

def register_child(email: str, password: str, full_name: str) -> NoReturn:
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Children (email, password, full_name) \
                   VALUES (?, ?, ?)", 
                   email, password, full_name)
    
    connection.commit()
    cursor.close()

def register_teacher(email: str, password: str, full_name: str) -> NoReturn:
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Teachers (email, password, full_name) \
                   VALUES (?, ?, ?)",
                   email, password, full_name)
    
    connection.commit()
    cursor.close()