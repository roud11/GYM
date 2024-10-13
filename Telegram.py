import os
from datetime import datetime
from dotenv import load_dotenv
import re
from Base import users_db, user_exists, schedule_reserve, get_user_data
from schedule import *
import telebot
from celery import Celery

load_dotenv()
bot_client = telebot.TeleBot(token=str(os.getenv('TOKEN')))

user_data = {}
app = Celery('tasks', broker='redis://localhost:6379/0')


@bot_client.message_handler(commands=['start'])
def send_welcome(message):
    bot_client.reply_to(message, "Привет! Используйте команду /register для начала регистрации.")


@bot_client.message_handler(commands=['register'])
def start_registration(message):
    chat_id = message.chat.id

    if not user_exists(chat_id):
        bot_client.send_message(chat_id,
                                "Для регистрации, пожалуйста, напишите свой номер телефона в формате: '79123456789'.")
        bot_client.register_next_step_handler(message, handle_phone_number)
    else:
        bot_client.send_message(chat_id, "Вы уже зарегистрированы. \nДля записи введите команду '/schedule'.")


def handle_phone_number(message):
    chat_id = message.chat.id
    if not re.match(r'^\d{11}$', message.text):
        bot_client.send_message(chat_id, "Неправильный формат номера телефона. Попробуйте еще раз.")
        bot_client.register_next_step_handler(message, handle_phone_number)  # Повторно ждем ввод номера телефона
        return

    user_data[chat_id] = {'phone': message.text}

    bot_client.send_message(chat_id,
                            "Для продолжения регистрации введите свои фамилию и имя в формате: 'Иванов Иван'.")
    bot_client.register_next_step_handler(message, handle_name)


def handle_name(message):
    chat_id = message.chat.id
    try:
        if chat_id not in user_data:
            bot_client.send_message(chat_id, "Пожалуйста, начните с команды /register и отправьте номер телефона.")
            return

        if len(message.text.split()) != 2:
            bot_client.send_message(chat_id, "Неправильный формат фамилии и имени. Попробуйте еще раз.")
            bot_client.register_next_step_handler(message, handle_name)  # Повторно ждем ввод имени
            return

        user_data[chat_id]['name'] = message.text

        users_db(chat_id, user_data[chat_id]['name'], user_data[chat_id]['phone'])

        bot_client.send_message(chat_id, "Регистрация успешно завершена. Данные сохранены. Для записи введите "
                                         "команду '/schedule'.")
        user_data[chat_id]['registration_success'] = True
    except Exception as e:
        bot_client.send_message(chat_id, f"Ошибка: {e}")
    finally:
        if chat_id in user_data and user_data[chat_id].get('registration_success', False):
            del user_data[chat_id]


@bot_client.message_handler(commands=['schedule'])
def choose_lesson(message):
    chat_id = message.chat.id
    schedule = check_schedule("https://mobifitness.ru/api/v6/club/1941/schedule.json")

    # Создаем клавиатуру с кнопками
    keyboard = telebot.types.InlineKeyboardMarkup()

    # Проходим по расписанию и создаем кнопки
    for lesson_num, lesson in schedule.items():
        print(f"Lesson data: {lesson}")  # Отладочный вывод данных о занятии
        datetime_obj = datetime.fromisoformat(lesson["Date and time"])
        # Добавляем кнопку для каждого занятия
        button = telebot.types.InlineKeyboardButton(
            f"{lesson_num}. {lesson['Lesson']} - {lesson['Trainer Name']} ({datetime_obj.strftime('%d.%m.%Y %H:%M')})",
            callback_data=str(lesson_num)
        )
        keyboard.add(button)

    # Отправляем сообщение с кнопками
    bot_client.send_message(chat_id, "Выберите занятие из списка:", reply_markup=keyboard)


@bot_client.callback_query_handler(func=lambda call: True)
def handle_lesson_choice(call):
    chat_id = call.message.chat.id
    lesson_number = call.data  # Получаем выбранный номер занятия

    schedule = check_schedule("https://mobifitness.ru/api/v6/club/1941/schedule.json")
    lesson = schedule[int(lesson_number)]
    user_id = str(chat_id)
    user_name, phone_number = get_user_data(user_id)

    # Данные для записи на занятие
    lesson_data = {
        'fio': user_name,
        'phone': phone_number,
        'scheduleId': lesson['ID'],
        'clubId': '1941'
    }

    # Записываем пользователя на занятие
    schedule_reserve(chat_id, lesson['ID'], lesson['Date and time'])
    bot_client.send_message(chat_id,
                            f"Вы успешно записаны на занятие: {lesson['Lesson']} с тренером {lesson['Trainer Name']} на"
                            f" {datetime.fromisoformat(lesson['Date and time']).strftime('%d.%m.%Y %H:%M')}.")
    execution_time = datetime.fromisoformat(lesson['Date and time']) - timedelta(hours=24)  # За сутки до занятия
    send_post_request.apply_async(args=[lesson_data, user_id, lesson], eta=execution_time)

    # Подтверждаем запись
    bot_client.send_message(chat_id,
                            f"Вы успешно выбрали занятие: {lesson['Lesson']} с тренером {lesson['Trainer Name']} на "
                            f"{datetime.fromisoformat(lesson['Date and time']).strftime('%d.%m.%Y %H:%M')}. "
                            f"Вам придёт уведомление, когда произойдёт запись.")


if __name__ == "__main__":
    bot_client.polling(none_stop=True)
