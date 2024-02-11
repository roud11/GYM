import sqlite3 as sql


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
        cursor = con.cursor()
        cursor.execute("""INSERT INTO Schedule_reserve
            (user_ids, schedule_id, date_time)
            VALUES(?, ?, ?)""", (user_id, schedule_id, time))


if __name__ == "__main__":
    create_db()
