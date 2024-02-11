import os
from datetime import datetime
from dotenv import load_dotenv
import re
from Base import users_db, user_exists, schedule_reserve
from schedule import *
import telebot
from telebot.types import Message

load_dotenv()
bot_client = telebot.TeleBot(token=str(os.getenv('TOKEN')))

user_data = {}


@bot_client.message_handler(commands=['start'])
def send_welcome(message):
    bot_client.reply_to(message, "Привет! Используйте команду /register для начала регистрации.")


@bot_client.message_handler(commands=['register'])
def start_registration(message):
    chat_id = message.chat.id

    if not user_exists(chat_id):
        bot_client.send_message(chat_id,
                                "Для регистрации напишите, пожалуйста, свой номер телефона в формате: '79000000000'.")
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
            print(user_data)
            del user_data[chat_id]


@bot_client.message_handler(commands=['schedule'])
def choose_lesson(message):
    chat_id = message.chat.id
    schedule = check_schedule("https://mobifitness.ru/api/v6/club/1941/schedule.json")
    user_schedule = ""
    for lesson in schedule:
        datetime_obj = datetime.fromisoformat(schedule[lesson]["Date and time"])
        user_schedule += f"{lesson}: {schedule[lesson]['Lesson']} - {datetime_obj.strftime('%d.%m.%Y')} в " \
                         f"{datetime_obj.strftime('%H:%M')}. Тренер: {schedule[lesson]['Trainer Name']} \n\n"
    bot_client.send_message(chat_id, "Вот список занятий, на которые можно записаться. Отправьте номер занятия, "
                                     "на которое желаете записаться.")
    bot_client.send_message(chat_id, user_schedule)
    print(schedule)
    bot_client.register_next_step_handler(message, handle_lesson_choice, schedule)


def handle_lesson_choice(message, schedule):
    chat_id = message.chat.id
    lesson_number = message.text

    if not lesson_number.isdigit():
        bot_client.send_message(chat_id, "Пожалуйста, введите номер занятия в виде цифры.")
        bot_client.register_next_step_handler(message, handle_lesson_choice)  # Повторно ждем ввод номера занятия
        return
    if not 1 <= int(lesson_number) <= len(schedule):  # Здесь max_len - максимальное значение номера занятия
        bot_client.send_message(chat_id, "Номер занятия введен некорректно. Пожалуйста, попробуйте еще раз.")
        bot_client.register_next_step_handler(message, handle_lesson_choice, schedule)  # Повторно ждем номер занятия
        return
    else:
        schedule_reserve(chat_id, schedule[int(lesson_number)]['ID'], schedule[int(lesson_number)]['Date and time'])
        bot_client.send_message(chat_id, f"Вы выбрали занятие {lesson_number}.")


if __name__ == "__main__":
    bot_client.polling(none_stop=True)
