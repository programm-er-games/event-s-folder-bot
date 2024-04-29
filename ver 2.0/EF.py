# TODO: добавить модульность и гибкость программе
import telebot
from telebot import types
from datetime import datetime

from config import event_reg_bot
from sql_EF import *
from check_formats_EF import *

bot = telebot.TeleBot(event_reg_bot)
users: dict[str, int] = {}  # format: [user id] - str: [current stage] - int
users_info: dict[str, list[str]] = {}  # format: [user id] - str: [ [info piece] - str ] - list


def get_datetime_now():
    day = str(datetime.now().day)
    month = str(datetime.now().month)
    hour = str(datetime.now().hour)
    minute = str(datetime.now().minute)
    second = str(datetime.now().second)
    day = ("0" + day) if 0 <= int(day) <= 9 else day
    month = ("0" + month) if 0 <= int(month) <= 9 else month
    hour = ("0" + hour) if 0 <= int(hour) <= 9 else hour
    minute = ("0" + minute) if 0 <= int(minute) <= 9 else minute
    second = ("0" + second) if 0 <= int(second) <= 9 else second
    result = day + "." + month + "." + str(datetime.now().year) + ", " + hour + ":" + minute + ":" + second
    return result


def get_question(event: str, number: int):
    qst = search_cond("questions", ["question", "output_type", "output_name"], event=event, id=number)
    if len(qst) != 0:
        need_to_check = False if qst[0][1] == "text" or qst[0][1] == "number" else True
        return qst[0][0], need_to_check, qst[0][2]
    else:
        return "end"


def next_stage(user_id: str, to: int = -2):
    global users
    if to == -2:
        users[user_id] += 1
    else:
        users[user_id] = to


# ---------------------------------------------------------


def queue_manager(message):
    global users, users_info
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = 0
        users_info[user_id] = []
    if users[user_id] == -1:
        del users[user_id]
        del users_info[user_id]
    # print(users)
    manager(message)


def manager(message):
    stage = users[str(message.from_user.id)]
    if stage == 0 and message.text == "/start":
        start(message)
    elif stage >= 3:
        out_stage(message)


# --------------------------------------------------------------------


def in_stage(user_id: str):
    stage = users[user_id]
    event = "RoboCup Russia Open"
    (text, need_to_check, out) = get_question(event, stage - 2)
    if text != "e" and need_to_check != "n" and out != "d":
        users_info[user_id].append(f"{need_to_check}, {out}")
        bot.send_message(user_id, text)
    else:
        end(user_id)


def out_stage(message):
    user_id = str(message.from_user.id)
    stage = users[user_id]
    temp = users_info[user_id][-1]
    stage_info = temp.split(", ")
    del users_info[user_id][-1], temp
    if stage_info[0] == "False":
        next_stage(user_id)
        in_stage(user_id)
    else:
        event = users_info[user_id][0].split(": ")[1]
        out_type = search_cond("questions", ["output_type"], event=event, id=stage - 2)
        result, text = "", ""
        match out_type:
            case "email":
                result = check_email_format(message.text)
            case "birth":
                result = check_birth_date_format(message.text)
        match result:
            case "correct, but error":
                text = ("Формат данных верный, но значения недостоверны.\n"
                        "Пожалуйста, напишите их так, как указано в Вашем паспорте")
            case "error":
                text = ("Формат данных неверный.\n"
                        "Пожалуйста, напишите их так, как указано в Вашем паспорте")
        bot.send_message(user_id, text)


@bot.callback_query_handler(func=lambda c: c.data == "yes")
def verify_yes(callback: types.CallbackQuery):
    global users
    bot.answer_callback_query(callback.id)
    if users[str(callback.from_user.id)] == 2:
        event = "RoboCup Russia Open"  # тестовое рабочее значение
        users_info[str(callback.from_user.id)].append(f"Мероприятие: {event}")
        next_stage(str(callback.from_user.id))
        in_stage(str(callback.from_user.id))


@bot.callback_query_handler(func=lambda c: c.data == "no")
def verify_no(callback: types.CallbackQuery):
    global users
    bot.answer_callback_query(callback.id)
    if users[str(callback.from_user.id)] == 2:
        text = "Ну, на нет - и суда нет. До свидания!"
        bot.send_message(callback.from_user.id, text, reply_markup=types.ReplyKeyboardRemove())
        next_stage(str(callback.from_user.id), -1)


@bot.callback_query_handler(func=lambda c: c.data == "event_list")
def event_list(callback: types.CallbackQuery):
    global users
    bot.answer_callback_query(callback.id)
    if users[str(callback.from_user.id)] == 1:
        names = search_all("events", "name")
        text = ""
        if len(names) > 1:
            text += "Вот список мероприятий, на которые можно записаться:\n\n"
            counter = 1
            for i in names:
                text += f"<b>{counter}. </b><u>{i[0]}</u>"
                text += ",\n"
                counter += 1
            text = text[0:-2]
            text += (".\n\nДля того, чтобы узнать о мероприятии, на которое Вы хотите записаться, "
                     "напишите его номер в списке")
            bot.send_message(callback.from_user.id, text, parse_mode='html')
        else:
            text += "Пока из доступных мероприятий Вы можете зарегистрироваться только на " \
                   f"\"{names[0][0]}\". Интересует?"
            yes = types.InlineKeyboardButton("Да", callback_data="yes")
            no = types.InlineKeyboardButton("Нет", callback_data="no")
            markup_choice = types.InlineKeyboardMarkup().add(yes, no)
            bot.send_message(callback.from_user.id, text, parse_mode='html', reply_markup=markup_choice)
            next_stage(str(callback.from_user.id))


def start(message):
    text = "Привет! Добро пожаловать в систему регистрации на мероприятия ЮФУ! " \
           "Я готов помочь Вам зарегистрироваться на интересующие Вас мероприятия. Давайте начнём!\n" \
           "<b>Нажмите на кнопку снизу этого сообщения, если хотите продолжить работу с ботом</b>"
    show_list = types.InlineKeyboardButton("Показать список мероприятий", callback_data="event_list")
    markup_show = types.InlineKeyboardMarkup().add(show_list)
    bot.send_message(message.from_user.id, text, reply_markup=markup_show, parse_mode='html')
    next_stage(str(message.from_user.id))


def end(user_id: str):
    text = "Замечательно! "
    event = users_info[user_id][0].split(": ")[1]
    data = search_cond("events", ["*"], name=event)
    text += f"Ты записан на мероприятие \"{data[0][0]}\", "
    text += f"которое пройдёт по адресу: {data[0][5]}."
    text += f"\n\n{data[0][1]}\n\n"
    text += f"Мероприятие пройдёт с {data[0][2]} по {data[0][3]}.\n"
    temp = data[0][4].split()
    contacts = ""
    for i in temp:
        contacts += i if not i.endswith(",") else i[0:-1]
    text += f"Если будут вопросы и/или пожелания, то обращайтесь по этим контактам:\n{contacts}"
    del temp, contacts
    bot.send_message(user_id, text)
    next_stage(user_id, -1)


if __name__ == '__main__':
    # print(search_all("events", "name"))
    raise SystemExit("Этот файл не должен запускаться как основной скрипт!")
