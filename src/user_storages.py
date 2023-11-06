import json
import sqlite3
import string
from datetime import time

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
telegram_id TEXT NOT NULL,
working_time TEXT NOT NULL,
department TEXT NOT NULL,
randomize BOOLEAN NOT NULL DEFAULT FALSE
)
''')
conn.commit()


class User:
    def __init__(self, name: string, personnel_number: string, telegram_id: string, working_time,
                 department: string = "ОРПО", randomize: bool = False):
        self.name = name
        self.personnel_number = personnel_number
        self.telegram_id = telegram_id
        self.working_time = working_time
        self.department = department
        self.randomize = randomize

    def isUserExist(self):
        try:
            cursor.execute(f"SELECT * FROM Users WHERE username = '{self.name}'")
        except sqlite3.OperationalError:
            return False
        if cursor.fetchone() is None:
            return False
        else:
            return True


def add_new_user(user: User) -> None:
    cursor.execute(
        f"INSERT INTO Users VALUES (NULL, '{user.name}', '{user.personnel_number}', '{user.telegram_id}', '{json.dumps(user.working_time, default=str)}', '{user.department}', '{user.randomize}')")
    conn.commit()


def remove_user_by_name(user: User) -> None:
    cursor.execute(f"DELETE FROM Users WHERE username = '{user.name}'")
    conn.commit()


def remove_user_by_personnel_number(user: User) -> None:
    cursor.execute(f"DELETE FROM Users WHERE personnel_number = '{user.personnel_number}'")
    conn.commit()


def remove_user_by_telegram_id(user: User) -> None:
    cursor.execute(f"DELETE FROM Users WHERE telegram_id = '{user.telegram_id}'")
    conn.commit()


def get_user_by_telegram_id(telegram_id: string) -> User:
    cursor.execute(f"SELECT * FROM Users WHERE telegram_id = '{telegram_id}'")
    user = cursor.fetchone()
    return User(user[1], user[2], user[3], json.loads(user[4]), user[5], user[6])


# на вход поступает такая строка "9:00-12:00 13:00-17:30"
def parse_schedule(schedule_str: str) -> dict:
    # Разбиваем строку по пробелу, чтобы получить два временных промежутка: рабочее время и обед
    first_work_period, second_work_period = schedule_str.split(" ")

    # Разбиваем каждый промежуток по символу "-", чтобы получить время начала и конца
    work_start_str, lunch_start_str = first_work_period.split("-")
    lunch_end_str, work_end_str, = second_work_period.split("-")

    # Преобразуем строки времени в объекты time
    work_start = time(int(work_start_str.split(":")[0]), int(work_start_str.split(":")[1]))
    work_end = time(int(work_end_str.split(":")[0]), int(work_end_str.split(":")[1]))
    lunch_start = time(int(lunch_start_str.split(":")[0]), int(lunch_start_str.split(":")[1]))
    lunch_end = time(int(lunch_end_str.split(":")[0]), int(lunch_end_str.split(":")[1]))

    # Возвращаем словарь с временами
    return {
        'work_start': work_start,
        'lunch_start': lunch_start,
        'lunch_end': lunch_end,
        'work_end': work_end
    }
