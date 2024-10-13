import sqlite3 as sql
from datetime import datetime, timedelta


def create_db():
    with sql.connect("users.db") as con:
        cursor = con.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
            user_ids TEXT PRIMARY KEY,
            user_name TEXT NOT NULL,
            phone_number TEXT NOT NULL
            )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Schedule_reserve(
                user_ids TEXT NOT NULL,
                schedule_id TEXT NOT NULL,
                date_time TEXT NOT NULL
                )""")


def users_db(user_id, name, phone):
    with sql.connect("users.db") as con:
        cursor = con.cursor()
        cursor.execute("""INSERT INTO Users
            (user_ids, user_name, phone_number)
            VALUES(?, ?, ?)""", (user_id, name, phone))


def user_exists(user_id):
    with sql.connect("users.db") as con:
        cursor = con.cursor()
        cursor.execute("SELECT 1 FROM Users WHERE user_ids = ?", (user_id,))
        result = cursor.fetchone()
        return bool(result)


def schedule_reserve(user_id, schedule_id, time):
    with sql.connect("users.db") as con:
        reserve_time = (datetime.fromisoformat(time) - timedelta(hours=24)).isoformat()
        cursor = con.cursor()
        cursor.execute("""INSERT INTO Schedule_reserve
            (user_ids, schedule_id, date_time)
            VALUES(?, ?, ?)""", (user_id, schedule_id, reserve_time))


def get_user_data(user_id):
    with sql.connect("users.db") as con:
        cursor = con.cursor()
        cursor.execute("SELECT user_name, phone_number FROM Users WHERE user_ids = ?", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            print(user_data[0], user_data[1])
            return user_data[0], user_data[1]
        else:
            return None, None


if __name__ == "__main__":
    create_db()
