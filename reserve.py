from datetime import datetime, timedelta
import Base as database


def process_schedule():
    current_time = datetime.now()
    future_time = (current_time + timedelta(hours=24))
    future_time = future_time.replace(tzinfo=current_time.tzinfo)
    # Считываем данные из таблицы Schedule_reserve
    with database.sql.connect("users.db") as con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Schedule_reserve")
        rows = cursor.fetchall()

        # Инициализируем словарь для хранения валидных записей
        valid_reserve = {}

        # Проходимся по каждой записи в таблице Schedule_reserve
        for row in rows:
            user_id = row[0]
            schedule_id = row[1]
            date_time_str = row[2]

            # Преобразуем строку времени в объект datetime
            date_time = datetime.fromisoformat(date_time_str).replace(tzinfo=current_time.tzinfo)

            # Проверяем, находится ли время занятия в допустимом диапазоне
            if date_time < future_time:
                # Удаляем запись из таблицы
                cursor.execute("DELETE FROM Schedule_reserve WHERE user_ids = ? AND schedule_id = ? AND date_time = ?",
                               (user_id, schedule_id, date_time_str))
                con.commit()
            else:
                # Получаем информацию о пользователе из таблицы Users
                cursor.execute("SELECT user_name, phone_number FROM Users WHERE user_ids = ?", (user_id,))
                user_data = cursor.fetchone()
                user_name = user_data[0]
                phone_number = user_data[1]

                # Сохраняем информацию в словаре
                valid_reserve[schedule_id] = {
                    "user_id": user_id,
                    "user_name": user_name,
                    "phone_number": phone_number,
                    "time": date_time_str
                }

    # Возвращаем валидные записи
    return valid_reserve


if __name__ == "__main__":
    valid_reserve = process_schedule()
    print(valid_reserve)
