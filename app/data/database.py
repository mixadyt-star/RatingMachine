from typing import NoReturn, List
import sqlite3
import json

from utils import security

connection = sqlite3.connect("main.db")
cursor = connection.cursor()

# Create table Blanks
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS Blanks (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
test_id INTEGER NOT NULL,
answers TEXT NOT NULL,
file TEXT NOT NULL
)
"""
)
connection.commit()

# Create table Tests
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS Tests (
id INTEGER PRIMARY KEY AUTOINCREMENT,
test_name VARCHAR(255) NOT NULL,
subject VARCHAR(255) NOT NULL,
class VARCHAR(255) NOT NULL,
answers TEXT NOT NULL,
questions TEXT
)
"""
)
connection.commit()

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
connection.commit()

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

# Create table WorkingTests
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS WorkingTests (
user_id INTEGER NOT NULL,
test_id INTEGER NOT NULL,
hash_code VARCHAR(255) PRIMARY KEY NOT NULL
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

def get_working_test(hash_code: str) -> tuple:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM WorkingTests \
                    WHERE hash_code = ?",
                    (hash_code,))
    data = cursor.fetchone()

    cursor.close()
    connection.close()

    return data

def get_test(id: int) -> tuple:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Tests \
                    WHERE id = ?",
                    (id,))
    data = cursor.fetchone()

    cursor.close()
    connection.close()

    return data

def get_questions(id: int) -> tuple:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT questions FROM Tests \
                    WHERE id = ?",
                    (id,))
    data = cursor.fetchone()
    cursor.close()
    connection.close()

    return data

def update_child(id: int, marks: list):
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("UPDATE Children SET \
                   marks = ? \
                   WHERE id = ?",
                   (json.dumps(marks), id))
    connection.commit()
    cursor.close()
    connection.close()

def get_child(id: int) -> tuple:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Children \
                    WHERE id = ?",
                    (id,))
    data = cursor.fetchone()
    cursor.close()
    connection.close()

    return data

def get_forms_by_class(class_: str) -> List[tuple]:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT form FROM Children \
                    WHERE form LIKE ? \
                    GROUP BY form",
                    (class_ + '%',))
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    return data

def get_blanks(test_data: List[tuple]) -> List[tuple]:
    data = []
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    for row in test_data:
        test_id = row[0]

        cursor.execute("SELECT * FROM Blanks \
                        WHERE test_id = ?",
                        (test_id,))
        data += cursor.fetchall()

    cursor.close()
    connection.close()

    return data

def get_tests(class_: str, subject: str) -> List[tuple]:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Tests \
                    WHERE class = ? \
                    AND subject = ?",
                    (class_, subject))
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

def delete_working_test(hash_code: str):
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM WorkingTests \
                   WHERE hash_code = ?", (hash_code,))
    
    connection.commit()
    cursor.close()
    connection.close()

def delete_test(id: int):
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Tests \
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

def check_test(id: int) -> bool:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Tests \
                    WHERE id = ?", (id,))
    alive = bool(cursor.fetchone())

    cursor.close()
    connection.close()

    return alive

def edit_questions(test_id: int, questions: str) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("UPDATE Tests SET \
                    questions = ? \
                    WHERE id = ?",
                    (questions, test_id))
    connection.commit()
    cursor.close()
    connection.close()

def edit_answers(test_id: int, answers: str) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("UPDATE Tests SET \
                   answers = ? \
                   WHERE id = ?",
                   (json.dumps(answers), test_id))
    connection.commit()
    cursor.close()
    connection.close()

def register_blank(user_id: int, test_id: int, answers: dict, file: str):
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Blanks (user_id, test_id, answers, file) \
                    VALUES (?, ?, ?, ?)",
                    (user_id, test_id, json.dumps(answers), file))
    connection.commit()
    cursor.close()
    connection.close()

def register_working_test(user_id: int, test_id: int, hash_code: str) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO WorkingTests (user_id, test_id, hash_code) \
                    VALUES (?, ?, ?)",
                    (user_id, test_id, hash_code))
    connection.commit()
    cursor.close()
    connection.close()

def register_test(test_name: str, subject: str, class_: str) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Tests (test_name, subject, class, answers) \
                    VALUES (?, ?, ?, ?)",
                    (test_name, subject, class_, json.dumps([""] * 26)))
    connection.commit()
    cursor.close()
    connection.close()

def register_child(full_name: str, form: str) -> NoReturn:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Children (full_name, form, marks) \
                    VALUES (?, ?, ?)",
                    (full_name, form, "[]"))
    
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

def get_stats_data() -> List[tuple]:
    connection = sqlite3.connect("main.db")
    cursor = connection.cursor()

    cursor.execute("SELECT marks, form FROM Children")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    return data