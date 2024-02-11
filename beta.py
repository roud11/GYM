import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import time
import Base as database
import schedule

main_url = 'https://mobifitness.ru/widget/792082?colored=1&lines=1&club=0&clubs=1941&grid30min=0&desc=0&direction=0' \
           '&group=0&trainer=0&room=0&age=&level=&activity=0&language=ru&custom_css=0&category_filter=2' \
           '&activity_filter=2&ren'
clubs_url = 'https://mobifitness.ru/api/v6/franchise/clubs.json'
reserve_url = 'https://mobifitness.ru/api/v6/account/reserve.json'


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
    return clubs  # тут нужно будет отправлять сообщением из словаря ключи, потом по ключу определять ID


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

            # Преобразуем строку времени в объект datetime с информацией о часовом поясе
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


def send_post_request(user_id, user_name, phone_number, schedule_id, club_id, scheduled_time):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(hours=24)  # Вычисляем разницу в 24 часа
    scheduled_time_minus_24h = scheduled_time - delta  # Вычитаем разницу из даты и времени
    if current_time >= scheduled_time_minus_24h:  # Проверяем, прошло ли уже более 24 часов
        headers = access_token()  # Получаем заголовки
        data = {
            'fio': user_name,
            'phone': phone_number,
            'scheduleId': schedule_id,
            'clubId': club_id
        }
        response = requests.post(reserve_url, headers=headers, data=data)
        return response.status_code
    else:
        return None  # Если не прошло еще 24 часа, возвращаем None


def schedule_post_requests(valid_reserve):
    for schedule_id, schedule_info in valid_reserve.items():
        schedule_time = datetime.datetime.fromisoformat(schedule_info['time'])
        schedule.every().day.at(schedule_time.strftime('%H:%M')).do(send_post_request,
                                                                    schedule_info['user_id'],
                                                                    schedule_info['user_name'],
                                                                    schedule_info['phone_number'],
                                                                    schedule_id,
                                                                    '1941',
                                                                    schedule_time).tag(schedule_id)


def registration():  # нужно дописать часть, где происходит регистрация
    valid_reserve = process_schedule()  # Получаем валидные записи из расписания
    schedule_post_requests(valid_reserve)
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверяем каждую минуту


if __name__ == "__main__":
    print(check_schedule("https://mobifitness.ru/api/v6/club/1941/schedule.json"))
    valid_reserve = process_schedule()
    print(valid_reserve)
