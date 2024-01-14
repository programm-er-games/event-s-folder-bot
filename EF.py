import telebot
from telebot import types

from about_func_EF import about
from sql_EF import clear_table, get_info_about_message, get_participant, \
    print_participants, print_events, prepare_event_text, check_tables, \
    prepare_event_list, get_event
from config import event_reg_bot
from check_formats_EF import check_email_format, check_birth_date_format

bot = telebot.TeleBot(event_reg_bot)
markup_remove = types.ReplyKeyboardRemove()

current_stage = "None"  # a variable responsible for the specific stage of the program
debug_stage = 0         # a variable responsible for the specific stage of passing the developer verification
participant_data = {
    "initials": {
        "surname": "",
        "name": "",
        "patronymic": ""
    },
    "command": "",
    "organization": "",
    "email": "",
    "birth_date": ""
}
event_data = {
    "name": "",
    "description": "",
    "date_start": "",
    "date_end": "",
    "contacts": "",
    "address": "",
}

is_force_exit = False
is_debug = False
is_blocked = False
is_finished = False


def manager(message):
    """
        This function determines which stage the user is currently at and what needs to be done at this stage.
        Returns True, if program has been finished, else False
    """
    global current_stage, debug_stage, is_debug
    if message.text == "/start":
        check_tables()
    # recording necessary info about sent message
    get_info_about_message(message.from_user.id, message.text) if __name__ != "__main__" else ...
    if message.text == "/about":
        about(message, bot, markup_remove)
    elif message.text == "/!admin":
        non_admin(message)
    elif message.text == "/admin" or is_debug or debug_stage > 0:
        admin(message)
    elif current_stage == "Подтверждение" or current_stage.startswith("Ввод данных: "):
        register(message)
    elif current_stage == "None" and message.text == "/start":
        start(message)
    elif current_stage not in ["None", "Старт", "Подтверждение"] and not current_stage.startswith("Ввод данных: "):
        bot.send_message(message.from_user.id, "<b>Извините, возникли неполадки в программе. "
                                               "Выполняю принудительное завершение работы...</b>",
                         parse_mode='html')
        bot.stop_bot()
        raise SystemError("Сбой в программе! Неправильное название этапа!")

    return is_finished


def admin(message):
    """
        This function is responsible for changing variables in the code through the bot,
        i.e. enter developer mode.
        For changes, you need to be verified that you are a developer.
        Nothing returns
    """
    global debug_stage, is_debug, is_blocked
    if not is_debug:
        match debug_stage:
            case 0:
                bot.send_message(message.from_user.id, "Ты разработчик? Докажи!")
                text = "<b>Первый вопрос:</b> как называется этот проект?"
                bot.send_message(message.from_user.id, text, parse_mode='html')
                debug_stage += 1

            case 1:
                if message.text == "Event's folder":
                    text = "Хорошо, <b>второй вопрос</b>: кто я?"
                    debug_stage += 1

                else:
                    if message.text == "Регистрация на мероприятия ЮФУ":
                        text = "Хорошая попытка, умник, <b>но нет</b>. Ты не разработчик."

                    elif message.text == "@event_register_bot":
                        text = "*саркастично хлопает* Молодец. Но ты не разработчик."

                    else:
                        text = "Не-а, даже не близко. Ты не разработчик."
                    is_debug = False
                    debug_stage = 0
                bot.send_message(message.from_user.id, text, parse_mode='html')

            case 2:
                if message.text == "?Я отк":
                    text = "Хахах, хорош. Это правильный ответ. А теперь последний вопрос: сколько у тебя друзей?"
                    debug_stage += 1

                else:
                    if message.text == "Программист":
                        text = "Хороош. Это БЫЛ правильный ответ. Ты не разработчик."

                    else:
                        text = "Не-а, даже не близко. Ты не разработчик."
                    is_debug = False
                    debug_stage = 0
                bot.send_message(message.from_user.id, text, parse_mode='html')

            case 3:
                if message.text == "1":
                    text = "Теперь я верю тебе. Ты разработчик."
                    debug_stage += 1
                    is_debug = True

                elif message.text == "2":
                    text = "Почти угадал. Но кое-где ты просчитался. Ты не разработчик."
                    is_debug = False
                    debug_stage = 0

                else:
                    text = "Не-а, даже не близко. Ты не разработчик."
                    is_debug = False
                    debug_stage = 0
                bot.send_message(message.from_user.id, text, parse_mode='html')

                if is_debug:
                    text = "Можно очистить данные из обоих таблиц командами /delev, /delpa и /delse (ты знаешь, " \
                           "за что они отвечают, поэтому будь осторожен). Если что, выйти из режима разработчика " \
                           "можно командой /!admin"
                    bot.send_message(message.from_user.id, text)
    else:
        if debug_stage == 5:
            message.text += "\n"
            info = []
            temp = ""
            is_start = False
            for i in message.text:
                if i == "\n" and is_start:
                    info.append(temp[1:])
                    temp = ""
                    is_start = False
                elif i == ":":
                    is_start = True
                elif is_start:
                    temp += i
            get_event(info[0], info[1], info[2], info[3], info[4], info[5])
            bot.send_message(message.from_user.id, f"Добавление мероприятия прошло успешно!")
            debug_stage -= 1

        elif message.text.startswith("/pr"):
            if message.text == "/prpa":
                bot.send_message(message.from_user.id, print_participants(), parse_mode='html')

            elif message.text == "/prev":
                bot.send_message(message.from_user.id, print_events(), parse_mode='html')

        elif message.text.startswith("/del"):
            import sqlite3
            try:
                if message.text == "/delev":
                    clear_table("events")
                elif message.text == "/delpa":
                    clear_table("participants")
                elif message.text == "/delse":
                    clear_table("sent_messages")

            except sqlite3.DatabaseError as e:
                result = "с ошибкой!"
                print(e)

            else:
                result = "успешно!"

            text = "Очистка данных таблицы проведена <b>" + result + "</b>"
            bot.send_message(message.from_user.id, text, parse_mode='html')

        elif message.text.startswith("/export"):
            from export_EF import export_to_xlsx
            temp = message.text.split(" ")
            result, dst = "", ""
            match len(temp):
                case 1:
                    result, dst = export_to_xlsx()

                case 2:
                    result, dst = export_to_xlsx(temp[1])

                case 3:
                    result, dst = export_to_xlsx(temp[1], temp[2])
            bot.send_message(message.from_user.id, result)
            temp_file = open(dst, "rb")
            bot.send_document(message.from_user.id, temp_file)
            temp_file.close()

        elif message.text == "/add_event":
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
            debug_stage += 1

        elif message.text == "/ahelp":
            bot.send_message(message.from_user.id,
                             "Доступные команды:\n\n\n"
                             "    <u>/ahelp</u> - admin help - показывает список команд, доступных "
                             "ТОЛЬКО в режиме разработчика;\n\n"
                             "    <u>/add_event</u> - добавляет мероприятие в таблицу events в БД;\n\n"
                             "    <u>/delev</u> - delete events - очищает таблицу students в БД;\n\n"
                             "    <u>/delpa</u> - delete participants - очищает"
                             " таблицу participants в БД;\n\n"
                             "    <u>/delse</u> - delete sent(_messages) - очищает таблицу "
                             "sent_messages в БД;\n\n"
                             "    <u>/prpa</u> - print participants - выводит данные таблицы "
                             "participants из БД;\n\n"
                             "    <u>/prev</u> - print events - выводит данные таблицы "
                             "events из БД;\n\n"
                             "    <u>/export</u> <u>[путь]</u> <u>[имя]</u> - производит экспорт данных в Excel-файл "
                             "по указанному пути в файл с указанным именем;\n\n"
                             "    <u>/!admin</u> - not admin - выход из режима разработчика "
                             "с возвращением на тот этап программы/сценария, на котором была вызвана "
                             "команда /admin.\n\n\n"
                             "Будьте осторожны! <b>Нерациональное использование команд может "
                             "повлиять на работу всего сценария!</b>",
                             parse_mode='html')

        elif message.text == "/admin":
            bot.send_message(message.from_user.id,
                             "Вы <b>уже</b> находитесь в режиме разработчика!",
                             parse_mode='html')


def non_admin(message):
    """
        This feature exits developer mode. Nothing returns
    """
    global debug_stage, is_debug
    bot.send_message(message.from_user.id, "Вы вышли из режима разработчика!"
                                           if debug_stage > 0 and is_debug
                                           else
                                           "Вы не должны были знать эту команду. Вы и так не являетесь разработчиком!")
    debug_stage = 0
    is_debug = False
    message.text = ""
    start(message) if current_stage == "None" and message.text == "/start" else register(message)


def finish_session(message: types.Message | types.CallbackQuery):
    """
        This function changes the variables to their initial values and add abiturient's data to DB. Nothing returns
    """
    global current_stage, is_debug, debug_stage, participant_data, is_force_exit
    get_participant(message.from_user.id, participant_data["initials"]["name"], participant_data["initials"]["surname"],
                    participant_data["initials"]["patronymic"], event_data["name"], participant_data["command"],
                    participant_data["organization"], participant_data["email"], participant_data["birth_date"]) \
        if not is_force_exit else ...
    current_stage = "None"
    participant_data["initials"]["name"] = ""
    participant_data["initials"]["surname"] = ""
    participant_data["initials"]["patronymic"] = ""
    participant_data["command"] = ""
    participant_data["organization"] = ""
    participant_data["email"] = ""
    participant_data["birth_date"] = ""
    is_debug = False
    debug_stage = 0
    is_force_exit = False


@bot.callback_query_handler(func=lambda c: c.data == "yes")
def verify_yes(callback: types.CallbackQuery):
    global current_stage
    bot.answer_callback_query(callback.id)
    if current_stage == "Подтверждение":
        text = "Хорошо! Для начала хотелось бы знать, " \
               "в какой школе/ВУЗе/кружке Вы обучаетесь/работаете?"
        event_data["name"] = "RoboCup Russia Open"
        bot.send_message(callback.from_user.id, text)
        current_stage = "Ввод данных: организация"


@bot.callback_query_handler(func=lambda c: c.data == "no")
def verify_no(callback: types.CallbackQuery):
    global current_stage, is_finished
    bot.answer_callback_query(callback.id)
    if current_stage == "Подтверждение":
        text = "Ну, на нет - и суда нет. До свидания!"
        bot.send_message(callback.from_user.id, text, reply_markup=markup_remove)
        finish_session(callback)
        is_finished = True


@bot.callback_query_handler(func=lambda c: c.data == "event_list")
def event_list(callback: types.CallbackQuery):
    global current_stage
    bot.answer_callback_query(callback.id)
    if current_stage == "Старт":
        text = prepare_event_list()
        yes = types.InlineKeyboardButton("Да", callback_data="yes")
        no = types.InlineKeyboardButton("Нет", callback_data="no")
        markup_choice = types.InlineKeyboardMarkup().add(yes, no)
        bot.send_message(callback.from_user.id, text, parse_mode='html', reply_markup=markup_choice)
        current_stage = "Подтверждение"


def start(message):
    global current_stage
    text = "Привет! Добро пожаловать в систему регистрации на мероприятия ЮФУ! " \
           "Я готов помочь Вам зарегистрироваться на интересующие Вас мероприятия. Давайте начнём!\n" \
           "<b>Нажмите на кнопку снизу этого сообщения, если хотите продолжить работу с ботом</b>"
    show_list = types.InlineKeyboardButton("Показать список мероприятий", callback_data="event_list")
    markup_show = types.InlineKeyboardMarkup().add(show_list)
    bot.send_message(message.from_user.id, text, reply_markup=markup_show, parse_mode='html')
    current_stage = "Старт"


def register(message):
    global is_finished, current_stage
    if current_stage == "Ввод данных: организация":
        participant_data["organization"] = message.text
        text = "Хорошо! Тогда напишите мне, как будет называться команда, " \
               "в которую Вы хотите вступить"
        bot.send_message(message.from_user.id, text, reply_markup=markup_remove)
        current_stage = "Ввод данных: название команды"

    elif current_stage == "Ввод данных: название команды":
        participant_data["command"] = message.text
        text = "Ага, записал. Тогда давайте запишем Ваши фамилию, имя и отчество"
        bot.send_message(message.from_user.id, text, reply_markup=markup_remove)
        current_stage = "Ввод данных: ФИО"

    elif current_stage == "Ввод данных: ФИО":
        temp = list(participant_data["initials"].keys())
        check = message.text.split(" ")
        if len(check) == len(temp) or len(temp) == 2:
            counter = 0
            for i in message.text:
                if i == " ":
                    counter += 1
                else:
                    participant_data["initials"][temp[counter]] += i
            text = f"Хорошо, <u>{participant_data['initials']['surname']}</u> " \
                   f"<u>{participant_data['initials']['name']}</u>. " \
                   "Теперь давайте запишем Ваш адрес электронной почты"
            current_stage = "Ввод данных: email"
        else:
            text = "Вы не дописали имя и отчество(при наличии)"
        bot.send_message(message.from_user.id, text, parse_mode='html', reply_markup=markup_remove)

    elif current_stage == "Ввод данных: email":
        result = check_email_format(message.text)
        match result:
            case "error":
                text = "Email введён <b>неправильно</b>. " \
                       "Введите, пожалуйста, корректный email"
            case message.text:
                text = "Хорошо, теперь введите дату своего рождения"
                participant_data["email"] = message.text
                current_stage = "Ввод данных: дата рождения"
            case _:
                raise SystemError("Некорректное поведение программы!")
        bot.send_message(message.from_user.id, text, parse_mode='html', reply_markup=markup_remove)

    elif current_stage == "Ввод данных: дата рождения":
        result = check_birth_date_format(message.text)
        match result:
            case "correct, but error":
                text = "Дата введена <b>правильно</b>, но значения <b>недостоверные</b>. " \
                       "Введите, пожалуйста, корректную дату рождения, указанную в Вашем паспорте"
            case "error":
                text = "Дата введена <b>неправильно</b>. " \
                       "Введите, пожалуйста, корректную дату рождения, указанную в Вашем паспорте"
            case message.text:
                text = "Хорошо! " + prepare_event_text("RoboCup Russia Open", False)
                participant_data["birth_date"] = message.text
                is_finished = True
            case _:
                raise SystemError("Некорректное поведение программы!")
        bot.send_message(message.from_user.id, text, reply_markup=markup_remove, parse_mode='html')
