# TODO: добавить модульность и гибкость программе
# TODO: добавить ветку админа
# TODO: АДМИН: вместо вопросов сделать ПИН-код для разработчика и организатора
# TODO: добавить проверку на повторное прохождение бота:
#  если один и тот же пользователь запускает бота, то предлагать другие варианты событий
#  (
#  хочет ли он изменить данные на запись,
#  хочет ли он записаться на другое/ещё одно мероприятие,
#  хочет ли он отменить заявку на мероприятие/(я)
#  )
# TODO: добавить возможность сортировки выводимых данных через "аргументы" команд
# TODO: добавить возможность добавления условий для удаления через "аргументы" команд
import telebot
from telebot import types
from telebot.util import smart_split

from config import event_reg_bot
from sql_EF import *
from check_formats_EF import *
from user_EF import User
from export_EF import send_file
from datetime_EF import get_datetime_now
from mail_EF import Mail


bot = telebot.TeleBot(event_reg_bot)
users: dict[str, User] = {}  # format: [user id] - str: [current stage] - int
event_dict: dict[int, str] = {}  # format: [event id] - int: [event name] - str
events_text = []
mail_handler = False


# ----------------------------------------------------------------------------


def queue_manager(message):
    global users
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = User(user_id, message.from_user.username)
    stage_manager(message)


def stage_manager(message):
    stage = users[str(message.from_user.id)].get_stage()
    insert("sent_messages",
           id=users[str(message.from_user.id)].get_id(),
           message_text=message.text,
           datetime=get_datetime_now())
    if stage == 0 and message.text == "/start":
        start(message)
    elif message.text == "/admin":
        users[str(message.from_user.id)].set_temp_value("stage", stage)
        users[str(message.from_user.id)].set_temp_value("admin", False)
        users[str(message.from_user.id)].next_stage(-3)
        admin(message)
    elif stage >= 3:
        out_stage(message)
    if stage <= -3:
        admin(message)


# ------------------------------------------------------------------------------------------


def open_mail():
    global mail_handler
    mail_handler = Mail()
    mail_handler.set_recipient("Right hand")


def close_mail():
    global mail_handler
    del mail_handler


# ----------------------------------------------------------------------------------------------------


def translate(word: str):
    translated_word = ""
    match word:
        case "email":
            translated_word = "почтового ящика"
        case "birth_date":
            translated_word = "даты рождения"
        case "integer":
            translated_word = "целого числа"
        case "initials":
            translated_word = "инициалов"
    return translated_word


# ----------------------------------------------------------------------------------------------------


def in_stage(user_id: str):
    global users
    text = users[user_id].get_question()
    if text != "end":
        bot.send_message(user_id, text, parse_mode='html')
    else:
        end(user_id)


def out_stage(message):
    global users
    user_id = str(message.from_user.id)
    stage = users[user_id].get_stage()
    text = ""
    if not users[user_id].is_being_checked():
        users[user_id].set_answer(message.text)
        users[user_id].next_stage()
        in_stage(user_id)
    else:
        event = users[user_id].get_event()
        out_type = search_cond("questions", ["output_type"], event=event, id=stage - 2)
        result = ""
        match out_type[0][0]:
            case "email":
                result = check_email_format(message.text)
            case "birth_date":
                result = check_birth_date_format(message.text)
            case "integer":
                result = check_integer_format(message.text)
            case "initials":
                result = check_initials_format(message.text)
        match result:
            case "correct, but error":
                text = (f"Формат данных {translate(out_type[0][0])} верный, но значения недостоверны.\n"
                        "Пожалуйста, напишите их так, как указано в Вашем паспорте")
            case "error":
                text = (f"Формат данных {translate(out_type[0][0])} неверный.\n"
                        "Пожалуйста, напишите их так, как указано в Вашем паспорте")
        if result == message.text:
            users[user_id].set_answer(message.text)
            users[user_id].next_stage()
            in_stage(user_id)
        else:
            bot.send_message(user_id, text)


# --------------------------------------------------------------------------------------------------------


def admin(message):
    global users, mail_handler
    current_user = users[str(message.from_user.id)]
    curr_stage = current_user.get_stage()
    if curr_stage == -3:
        if message.text == "/admin" and current_user.get_temp_value("admin") is False:
            text = "Если Вы разработчик или доверенное лицо, то введите специальный код, высланный на почту"
            open_mail()
            mail_handler.send_code()
            bot.send_message(message.from_user.id, text, parse_mode='html')
            current_user.set_temp_value("tries_counter", 3)
        else:
            if mail_handler.check_code(message.text):
                current_user.set_temp_value("admin", True)
                text = ("<b>Всё верно!</b>\n"
                        "Экспортировать данные из базы данных можно командой /export\n"
                        "Другие доступные команды можно просмотреть командой /ahelp")
                bot.send_message(message.from_user.id, text, parse_mode='html')
                current_user.next_stage(-4)
            else:
                current_user.set_temp_value(
                    "tries_counter",
                    current_user.get_temp_value("tries_counter") - 1
                )
                current_user.set_temp_value("admin", False)
                if current_user.get_temp_value("tries_counter") > 0:
                    text = ("<b>Неверно!</b>\n"
                            f"У Вас осталось попыток для подтверждения: "
                            f"{current_user.get_temp_value('tries_counter')}!")
                    bot.send_message(message.from_user.id, text, parse_mode='html')
                    current_user.next_stage(-4)
                else:
                    text = ("<b>Неверно!</b>\n"
                            "Вы исчерпали все свои попытки! Вы не являетесь доверенным лицом "
                            "и не имеете доступа к данной команде!\n"
                            "<b>Возврат к последнему этапу...</b>")
                    back_to = current_user.get_temp_value("stage")
                    current_user.next_stage(back_to)
                    bot.send_message(message.from_user.id, text, parse_mode='html')
    elif curr_stage == -4 and current_user.get_temp_value("admin"):
        stage = current_user.get_temp_value("admin_stage")
        if stage is False or stage == "":
            match message.text:
                case "/export":
                    send_file(bot, message.from_user.id)
                case "/add_event":
                    text = "Для добавления реального мероприятия скопируйте сообщение-форму, " \
                           "которое сейчас будет выслано, вставьте в поле для ввода сообщений " \
                           "и \"заполните\" её соответственно полям (без запятых после значений)"
                    bot.send_message(message.from_user.id, text, parse_mode='html')
                    text = "<b>Название:</b> \n" \
                           "<b>Описание:</b> \n" \
                           "<b>Начало проведения:</b> \n" \
                           "<b>Конец проведения:</b> \n" \
                           "<b>Контакты:</b> \n" \
                           "<b>Адрес проведения:</b> "
                    bot.send_message(message.from_user.id, text, parse_mode='html')
                    current_user.set_temp_value("admin_stage", "/add_event")
                # case "/delev":
                #     ...
                # case "/delpa":
                #     ...
                # case "/delqs":
                #     ...
                case "/delse":
                    delete_all("sent_messages", "*")
                    current_user.set_temp_value("admin_stage", "")
                case "/prev":
                    data = search_all("events", "*")
                    text = "Вот список таблицы <b>events</b>:\n\n"
                    counter = 1
                    for rows in data:
                        text += f" {counter}.\n"
                        text += f"   Имя мероприятия: <u>{rows[0]}</u>\n"
                        text += f"   Описание:\n{rows[1]}\n"
                        text += f"   Дата проведения: {rows[2]} - {rows[3]},\n"
                        text += f"   Адрес проведения: {rows[5]},\n"
                        text += f"   Контакты:\n{rows[4]}\n"
                        text += f"   Дата добавления мероприятия: {rows[6]}"
                        counter += 1
                    bot.send_message(message.from_user.id, text, parse_mode='html')
                    current_user.set_temp_value("admin_stage", "")
                    del counter, text
                case "/prpa":
                    data = search_all("participants", "*")
                    text = "Вот список таблицы <b>participants</b>:\n\n"
                    counter = 1
                    for rows in data:
                        text += f" {counter}.\n"
                        text += f"   ID пользователя: {rows[0]}\n"
                        text += f"   Имя пользователя: {rows[1]}\n"
                        text += f"   ФИО: {rows[2]} {rows[3]} {rows[4]}\n"
                        text += f"   Участник мероприятия: {rows[5]}\n"
                        text += f"   Другая информация:\n"
                        temp = ""
                        for i in rows[6]:
                            temp += i
                            text += f"     {temp}"
                            temp = ""
                        del temp
                        text += f"\n   Дата добавления участника: {rows[7]}"
                        counter += 1
                    bot.send_message(message.from_user.id, text, parse_mode='html')
                    current_user.set_temp_value("admin_stage", "")
                    del counter, text, data
                # case "/prqs":
                #     events_data = search_all("questions", "event")
                #     text = "Вот список таблицы <b>questions</b>, отсортированный по мероприятиям:\n\n"
                #     counter = 1
                #     for i in events_data:
                #         data = search_cond("questions",
                #                            ["id", "question", "output_type", "output_name"],
                #                            event=i[0], id=counter)
                #         text += f" {counter}. {i[0]}\n"
                #         text += f"   Порядковый номер вопроса: {data[0]}\n"
                #         text += f"   Вопрос: {data[1]}\n"
                #         text += f"   Тип ответа на вопрос: {data[2]}\n"
                #         text += f"   Предмет вопроса: {data[3]}\n"
                #         counter += 1
                #     bot.send_message(message.from_user.id, text, parse_mode='html')
                #     current_user.set_temp_value("admin_stage", "")
                #     del counter, text, events_data
                case "/ahelp":
                    text = ("Доступные команды:\n\n\n"
                            "    <u>/ahelp</u> - admin help - показывает список команд, доступных "
                            "ТОЛЬКО в режиме разработчика;\n\n"
                            "    <u>/add_event</u> - добавляет мероприятие в таблицу events в БД;\n\n"
                            # "    <u>/delev</u> - очищает таблицу events в БД;\n\n"
                            # "    <u>/delpa</u> - очищает таблицу participants в БД;\n\n"
                            # "    <u>/delqs</u> - очищает таблицу questions в БД;\n\n"
                            "    <u>/delse</u> - очищает таблицу sent_messages в БД;\n\n"
                            "    <u>/prpa</u> - выводит данные таблицы participants из БД;\n\n"
                            "    <u>/prev</u> - выводит данные таблицы events из БД;\n\n"
                            # "    <u>/prqs</u> - выводит данные таблицы questions из БД;\n\n"
                            "    <u>/export</u> - производит экспорт данных в Excel-файл "
                            "и присылает результат отдельным сообщением;\n\n"
                            "    <u>/!admin</u> - выход из режима разработчика "
                            "с возвращением на тот этап программы/сценария, на котором была вызвана "
                            "команда /admin.\n\n\n"
                            "Будьте осторожны! <b>Нерациональное использование команд может "
                            "повлиять на работу всего сценария!</b>")
                    bot.send_message(message.from_user.id, text, parse_mode='html')
                    current_user.set_temp_value("admin_stage", "")
                    del text
                case "/!admin":
                    bot.send_message(message.from_user.id,
                                     "Вы вышли из режима разработчика!\n"
                                     "<b>Возврат к последнему этапу...</b>",
                                     parse_mode='html')
                    back_to = current_user.get_temp_value("stage")
                    current_user.next_stage(back_to)
        elif stage == "/add_event":
            data = check_event_info_format(message.text)
            if data == "error":
                text = ("<b><u>Что-то пошло не так!</u></b>\n"
                        "Проверьте ещё раз корректность оформления и заполнения самой формы!")
                bot.send_message(message.from_user.id, text, parse_mode='html')
                del text
            else:
                insert("events",
                       name=data["name"],
                       description=data["description"],
                       date_start=data["date_start"],
                       date_end=data["date_end"],
                       contacts=data["contacts"],
                       address=data["address"])
                bot.send_message(message.from_user.id,
                                 "<b>Мероприятие успешно записано в БД!</b>",
                                 parse_mode='html')


# -----------------------------------------------------------------------------------------


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
    text += f"Вы хотите записаться на это мероприятие? Для ответа нажмите соответствующую на кнопку"
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
            # print(users)
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
            texts = smart_split(text)
            events_text[0] = text
            events_text[1] = markup_choice
            message_id = 0
            if len(texts) > 1:
                for i in texts:
                    bot.send_message(callback.from_user.id, i, parse_mode='html')
                message = bot.send_message(callback.from_user.id, "Выбирайте мероприятие из списков выше")
                message_id = message.id
            else:
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
            users[user_id].set_event(names[0][0])
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
    users[user_id].add_user_to_db()
    del users[user_id]
    # print(users)


if __name__ == '__main__':
    # print(search_all("events", "name"))
    raise SystemExit("Этот файл не должен запускаться как основной скрипт!")
