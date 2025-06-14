import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import time
import Base as database
from celery import Celery
from Telegram import bot_client

main_url = 'https://mobifitness.ru/widget/792082?colored=1&lines=1&club=0&clubs=1941&grid30min=0&desc=0&direction=0' \
           '&group=0&trainer=0&room=0&age=&level=&activity=0&language=ru&custom_css=0&category_filter=2' \
           '&activity_filter=2&ren'
clubs_url = 'https://mobifitness.ru/api/v6/franchise/clubs.json'
reserve_url = 'https://mobifitness.ru/api/v6/account/reserve.json'

app = Celery('tasks', broker='redis://localhost:6379/0')


def access_token():
    soup_token = bs(requests.get(main_url).text, 'html.parser')
    scripts = soup_token.find_all('script')

    for script in scripts:
        if 'accesstok' in script.text:
            script_text = script.text
            access_start = script_text.find('accesstok') + len('accesstok') + 3
            access_end = script_text.find(',', access_start) - 1
            access_token = script_text[access_start:access_end]

    headers = {'Authorization': 'Bearer ' + access_token}
    return headers


def choose_club():
    headers = access_token()
    req = requests.get(clubs_url, headers=headers)
    clubs = {}
    for club in req.json():
        clubs[club['title']] = club['id']
    return clubs  # тут нужно будет отправлять сообщением из словаря ключи, потом по ключу определять ID клуба


def check_schedule(schedule_url):
    headers = access_token()
    schedule_json = requests.get(schedule_url, headers=headers).json()
    week_schedule = {}
    number = 1
    for work in schedule_json['schedule']:
        if work['preEntry']:
            week_schedule[number] = {'ID': work['id'], 'Date and time': work['datetime'],
                                     'Lesson': work['activity']['title'],
                                     'Trainer Name': work['trainers'][0]['title'],
                                     'change': work['change']}
            number += 1
    return week_schedule


def process_schedule():
    current_time = datetime.now() + timedelta(seconds=30)
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

            # Преобразуем строку времени в объект datetime с информацией о часовом поясе
            date_time = datetime.fromisoformat(date_time_str).replace(tzinfo=current_time.tzinfo)

            # Проверяем, находится ли время занятия в допустимом диапазоне
            if date_time < current_time:
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


@app.task
def send_post_request(data, chat_id, lesson):
    headers = access_token()
    flag = False
    while not flag:
        response = requests.post(reserve_url, headers=headers, data=data)
        if response.status_code == 200:
            bot_client.send_message(chat_id,
                                    f"Вы успешно записаны на занятие {lesson['Lesson']}.")
            flag = True
        print(response.status_code)


if __name__ == "__main__":
    print(check_schedule("https://mobifitness.ru/api/v6/club/1941/schedule.json"))
    valid_reserve = process_schedule()
    print(valid_reserve)
