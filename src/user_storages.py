import sqlite3
import string

# create new sqlite connection
conn = sqlite3.connect('users.db')
# create cursor
cursor = conn.cursor()
# Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
personnel_number TEXT NOT NULL,
telegram_id TEXT NOT NULL
)
''')
conn.commit()


class User:
    def __init__(self, name: string, personnel_number: string, telegram_id: string):
        self.name = name
        self.personnel_number = personnel_number
        self.telegram_id = telegram_id

    def isUserExist(self):
        cursor.execute(f"SELECT * FROM Users WHERE telegram_id = '{self.telegram_id}'")
        if cursor.fetchone() is None:
            return False
        else:
            return True


def add_new_user(name: string, personnel_number: string, telegram_id: string) -> None:
    cursor.execute(f"INSERT INTO Users VALUES (NULL, '{name}', '{personnel_number}', '{telegram_id}')")
    conn.commit()


def remove_user_by_name(name: string) -> None:
    cursor.execute(f"DELETE FROM Users WHERE username = '{name}'")
    conn.commit()


def remove_user_by_personnel_number(personnel_number: string) -> None:
    cursor.execute(f"DELETE FROM Users WHERE personnel_number = '{personnel_number}'")
    conn.commit()


def remove_user_by_telegram_id(telegram_id: string) -> None:
    cursor.execute(f"DELETE FROM Users WHERE telegram_id = '{telegram_id}'")
    conn.commit()


def get_user_by_telegram_id(telegram_id: string) -> User:
    cursor.execute(f"SELECT * FROM Users WHERE telegram_id = '{telegram_id}'")
    user = cursor.fetchone()
    return User(user[1], user[2], user[3])
