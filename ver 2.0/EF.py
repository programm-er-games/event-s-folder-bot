# TODO: добавить модульность и гибкость программе
# TODO: добавить ветку админа
# TODO: добавить проверку на повторное прохождение бота:
#  если один и тот же пользователь запускает бота, то предлагать другие варианты событий
#  (
#  хочет ли он изменить данные на запись,
#  хочет ли он записаться на другое/ещё одно мероприятие,
#  хочет ли он отменить заявку на мероприятие/(я)
#  )
import telebot
from telebot import types
from telebot.util import smart_split

from config import event_reg_bot
from sql_EF import *
from check_formats_EF import *
from user_EF import User

bot = telebot.TeleBot(event_reg_bot)
users: dict[str, User] = {}  # format: [user id] - str: [current stage] - int
event_dict: dict[int, str] = {}  # format: [event id] - int: [event name] - str
events_text = []


# ----------------------------------------------------------------------------


def queue_manager(message):
    global users
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = User(user_id, message.from_user.username)
    # if users[user_id] == -1:
    #     del users[user_id]
    # print(users)
    manager(message)


def manager(message):
    stage = users[str(message.from_user.id)].get_stage()
    if stage == 0 and message.text == "/start":
        start(message)
    elif stage >= 3:
        out_stage(message)


# ----------------------------------------------------------------------------------------------------


def in_stage(user_id: str):
    global users
    text = users[user_id].get_question()
    if text != "end":
        bot.send_message(user_id, text)
    else:
        end(user_id)


def out_stage(message):
    global users
    user_id = str(message.from_user.id)
    stage = users[user_id].get_stage()
    if not users[user_id].is_being_checked():
        users[user_id].set_answer(message.text)
        users[user_id].next_stage()
        in_stage(user_id)
    else:
        event = users[user_id].get_event()
        out_type = search_cond("questions", ["output_type"], event=event, id=stage - 2)
        result, text = "", ""
        match out_type[0][0]:
            case "email":
                result = check_email_format(message.text)
            case "birth":
                result = check_birth_date_format(message.text)
            case "integer":
                result = check_integer_format(message.text)
        match result:
            case "correct, but error":
                text = (f"Формат данных {out_type[0][0]} верный, но значения недостоверны.\n"
                        "Пожалуйста, напишите их так, как указано в Вашем паспорте")
            case "error":
                text = (f"Формат данных {out_type[0][0]} неверный.\n"
                        "Пожалуйста, напишите их так, как указано в Вашем паспорте")
        if result == message.text:
            users[user_id].next_stage()
            in_stage(user_id)
        else:
            bot.send_message(user_id, text)


# --------------------------------------------------------------------------------------------------------


@bot.callback_query_handler(func=lambda c: isinstance(c.data, int) and 1 <= c.data)
def show_event_info(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id)
    event = event_dict[int(callback.data)]
    user_id = str(callback.from_user.id)
    event_info = search_cond("events", ["*"], name=event)
    text = f"Имя мероприятия: <u>{event_info[0][0]}</u>\n"
    text += f"Описание:\n{event_info[0][1]}\n"
    text += f"Дата проведения: {event_info[0][2]} - {event_info[0][3]},\n"
    text += f"Адрес проведения: {event_info[0][5]},\n"
    text += f"Контакты:\n{event_info[0][4]}\n"
    text += f"Вы хотите записаться на это мероприятие? Если хотите, то напишите \"Да\", иначе - \"Нет\""
    yes = types.InlineKeyboardButton("Да", callback_data="ch_yes")
    no = types.InlineKeyboardButton("Нет", callback_data="ch_no")
    markup_choice = types.InlineKeyboardMarkup().add(yes, no)
    bot.edit_message_text(text, callback.from_user.id, users[user_id].get_list_id(), reply_markup=markup_choice)
    users[user_id].set_event(event)


@bot.callback_query_handler(func=lambda c: c.data == "yes" or c.data == "ch_yes")
def verify_yes(callback: types.CallbackQuery):
    global users
    bot.answer_callback_query(callback.id)
    user_id = str(callback.from_user.id)
    if users[user_id].get_stage() == 2:
        if callback.data == "yes":
            event = "RoboCup Russia Open"  # тестовое рабочее значение
            users[user_id].set_event(event)
        users[user_id].next_stage()
        in_stage(str(callback.from_user.id))


@bot.callback_query_handler(func=lambda c: c.data == "no" or c.data == "ch_no")
def verify_no(callback: types.CallbackQuery):
    global users, events_text
    bot.answer_callback_query(callback.id)
    user_id = str(callback.from_user.id)
    if users[user_id].get_stage() == 2:
        if callback.data == "no":
            text = "Ну, на нет - и суда нет. До свидания!"
            bot.send_message(callback.from_user.id, text, reply_markup=types.ReplyKeyboardRemove())
            del users[user_id]
        elif callback.data == "ch_no":
            users[user_id].set_event("")
            bot.edit_message_text(events_text[0], user_id, users[user_id].get_list_id(),
                                  parse_mode='html', reply_markup=events_text[1])


@bot.callback_query_handler(func=lambda c: c.data == "event_list")
def print_event_list(callback: types.CallbackQuery):
    global users, event_dict, events_text
    bot.answer_callback_query(callback.id)
    user_id = str(callback.from_user.id)
    if users[user_id].get_stage() == 1:
        names = search_all("events", "name")
        if len(names) > 1:
            text = "Вот список мероприятий, на которые можно записаться:\n\n"
            counter = 1
            markup_choice = types.InlineKeyboardMarkup(row_width=5)
            for i in names:
                text += f"<b>{counter}. </b><u>{i[0]}</u>,\n"
                event_dict[counter] = i[0]
                counter += 1
            for i in range(1, counter + 1):
                markup_choice.add(types.InlineKeyboardButton(counter, callback_data=counter))
            text = text[0:-2]
            text += (".\n\nДля того, чтобы узнать о мероприятии, на которое Вы хотите записаться, "
                     "нажмите на кнопку с его цифрой в списке")
            smart_split(text)
            events_text[0] = text
            events_text[1] = markup_choice
            message = bot.send_message(callback.id, text, parse_mode='html', reply_markup=markup_choice)
            message_id = message.id
            users[user_id].set_list_id(message_id)
        else:
            text = "Пока из доступных мероприятий Вы можете зарегистрироваться только на " \
                   f"\"{names[0][0]}\". Интересует?"
            yes = types.InlineKeyboardButton("Да", callback_data="yes")
            no = types.InlineKeyboardButton("Нет", callback_data="no")
            markup_choice = types.InlineKeyboardMarkup().add(yes, no)
            bot.send_message(callback.from_user.id, text, parse_mode='html', reply_markup=markup_choice)
            users[user_id].next_stage()
    # print(users[user_id].get_stage())


# ----------------------------------------------------------------------------------------------------------


def start(message):
    text = "Привет! Добро пожаловать в систему регистрации на мероприятия ЮФУ! " \
           "Я готов помочь Вам зарегистрироваться на интересующие Вас мероприятия. Давайте начнём!\n" \
           "<b>Нажмите на кнопку снизу этого сообщения, если хотите продолжить работу с ботом</b>"
    show_list = types.InlineKeyboardButton("Показать список мероприятий", callback_data="event_list")
    markup_show = types.InlineKeyboardMarkup().add(show_list)
    bot.send_message(message.from_user.id, text, reply_markup=markup_show, parse_mode='html')
    # print(users[str(message.from_user.id)].get_stage())
    users[str(message.from_user.id)].next_stage()
    # print(users[str(message.from_user.id)].get_stage())


def end(user_id: str):
    text = "Замечательно! "
    event = users[user_id].get_event()
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
    bot.send_message(user_id, text)
    del users[user_id]


if __name__ == '__main__':
    # print(search_all("events", "name"))
    raise SystemExit("Этот файл не должен запускаться как основной скрипт!")