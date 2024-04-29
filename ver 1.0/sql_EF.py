import sqlite3
from datetime import datetime

conn = sqlite3.Connection("C:\\Windows.old\\Users\\User\\Documents\\GitHub\\event-s-folder-bot\\event_register.db", check_same_thread=False)
cur = conn.cursor()


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
    result = day + "." + month + "." + str(datetime.now().year) + " " + hour + ":" + minute + ":" + second
    return result


current_datetime = get_datetime_now()


def check_tables():
    """
        This function creates tables if they have not been created or not exist
    """
    cur.execute("""CREATE TABLE IF NOT EXISTS events (
        name        TEXT UNIQUE
                         NOT NULL,
        description TEXT,
        date_start  TEXT NOT NULL,
        date_end    TEXT NOT NULL,
        contacts    TEXT NOT NULL,
        address     TEXT NOT NULL,
        add_date    TEXT NOT NULL
    )""")
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS participants (
        id           INTEGER NOT NULL
                             UNIQUE,
        name         TEXT UNIQUE
                          NOT NULL,
        surname      TEXT UNIQUE
                          NOT NULL,
        patronymic   TEXT,
        event_partic TEXT NOT NULL,
        command      TEXT NOT NULL,
        organization TEXT NOT NULL,
        email        TEXT NOT NULL
                          UNIQUE,
        birth_date   TEXT NOT NULL,
        add_date     TEXT NOT NULL
    )""")
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS sent_messages (
        id             INTEGER NOT NULL,
        message_text   TEXT,
        write_datetime TEXT    NOT NULL
    )""")
    conn.commit()


def prepare_event_text(event: str, is_start: bool):
    # try:
    text = ""
    name = cur.execute(f"SELECT name FROM events WHERE name == \"{event}\"").fetchone()[0]
    desc = cur.execute(f"SELECT description FROM events WHERE name = \"{event}\"").fetchone()[0]
    date_start = cur.execute(f"SELECT date_start FROM events WHERE name = \"{event}\"").fetchone()[0]
    date_end = cur.execute(f"SELECT date_end FROM events WHERE name = \"{event}\"").fetchone()[0]
    contacts = cur.execute(f"SELECT contacts FROM events WHERE name = \"{event}\"").fetchone()[0]
    address = cur.execute(f"SELECT address FROM events WHERE name = \"{event}\"").fetchone()[0]
    if is_start:
        text += f"Имя мероприятия: <u>{name}</u>\n"
        text += f"Описание:\n{desc}\n"
        text += f"Дата проведения: {date_start} - {date_end},\n"
        text += f"Адрес проведения: {address},\n"
        text += f"Контакты:\n{contacts}\n"
        text += f"Вы хотите записаться на это мероприятие? Если хотите, то напишите \"Да\", иначе - \"Нет\""
    else:
        text += f"Ты записан на мероприятие \"{name}\", "
        text += f"которое пройдёт по адресу: {address}."
        text += f"\n\n{desc}\n\n"
        text += f"Мероприятие пройдёт с {date_start} по {date_end}.\n"
        temp = ""
        for i in contacts:
            temp += ("  " + i) if contacts.index(i) == contacts[0] else ((i + "  ") if i == "\n" else i)
        contacts = temp
        text += f"Если будут вопросы и/или пожелания, то обращайтесь по этим контактам:\n{contacts}"
    return text
    # except TypeError:
    #     print("Error")
    #     return "<b><u>Никаких мероприятий нет!</u></b>"


def prepare_event_list():
    names = cur.execute("SELECT name FROM events").fetchall()[0]
    text = "Вот список мероприятий, на которые можно записаться:\n\n"
    if len(names) > 1:
        for i in list(names):
            text += f"<b>{names.index(i) + 1}. </b><u>{i}</u>"
            text += ",\n" if i != names[names.index(i)] else ".\n\n"
        text += "Для того, чтобы узнать о мероприятии, на которое Вы хотите записаться, напишите его номер в списке"
    else:
        text = "Пока из доступных мероприятий Вы можете зарегистрироваться только на " \
               f"\"{names[0]}\". Интересует?"
    return text


def print_events():
    cur.execute("SELECT * FROM events")
    data = cur.fetchall()
    text = "Вот список записанных мероприятий:\n"
    for i in data:
        text += f"  <b>{data.index(i) + 1}-е мероприятие</b>:\n"
        i = list(i)
        text += f"    <b>Название:</b> {i[0]},\n" \
                f"    <b>Описание:</b> {i[1]},\n" \
                f"    <b>Начало проведения:</b> {i[2]},\n" \
                f"    <b>Конец проведения:</b> {i[3]},\n" \
                f"    <b>Контакты:</b> {i[4]},\n" \
                f"    <b>Адрес проведения:</b> {i[5]},\n" \
                f"    <b>Дата добавления в список:</b> {i[6]}.\n\n"
    return text


def get_event(name: str, description: str,
              date_start: str, date_end: str,
              contacts: str, address: str):
    """
        Adds data about events from arguments
    """
    try:
        cur.execute("INSERT INTO events (name, description, date_start, "
                    "date_end, contacts, address, add_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, description, date_start,
                     date_end, contacts, address, current_datetime))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Это мероприятие уже существует в таблице!")


def print_participants():
    cur.execute("SELECT * FROM participants")
    data = cur.fetchall()
    text = "Вот список записанных участников:\n"
    rows = [i for i in data]
    values = []
    for i in rows:
        for j in i:
            values.append(j)
    text_values = ["<b>Имя:</b> ", "<b>Фамилия:</b> ", "<b>Отчество:</b> ",
                   "<b>Мероприятие, в котором участвует:</b> ",
                   "<b>Команда на мероприятии, в которой состоит:</b> ", "<b>Организация:</b> ",
                   "<b>Email:</b> ", "<b>Дата рождения:</b> "]
    if len(values) > 0:
        for i in range(0, len(text_values) - 1):
            text += f"  {text_values[i]}{values[i]},\n"
    else:
        text = "<b><u>Никаких участников нет!</u></b>"
    return text


def get_participant(user_id: int, name: str, surname: str, patronymic: str,
                    event_partic: str, command: str, organization: str,
                    email: str, birth_date: str):
    """
        Adds data about participants from arguments
    """
    try:
        cur.execute("INSERT INTO participants (id, name, surname, patronymic, "
                    "event_partic, command, organization, email, birth_date, add_date) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, name, surname, patronymic,
                     event_partic, command,
                     organization, email, birth_date, current_datetime))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Этот пользователь уже существует в таблице!")


def get_info_about_message(user_id: int, text: str):
    """
        Adds data about sent message from arguments
    """
    cur.execute("INSERT INTO sent_messages (id, message_text, write_datetime) VALUES (?, ?, ?)",
                (user_id, text, current_datetime))
    conn.commit()


def clear_table(table: str):
    """
        Clear the table specified in the arguments. Returns str, if the operation was successful
    """
    if table in ["participants", "events", "sent_messages"]:
        cur.execute(f"DELETE FROM {table}")
        data = cur.fetchall()
        conn.commit()
        return data
    else:
        return False


def test():
    """
        Test function. Do not use in main program
    """
    while True:
        command = input("Введите команду: ")
        if command == "clear":
            table = input("Какую таблицу Вы хотите очистить? ")
            r = clear_table(table)
            print(r)
        elif command == "pr_ev_t":
            is_start = input("(T/F, True/False) -> is_start: bool = ")
            if is_start.startswith("T"):
                is_start = True
            elif is_start.startswith("F"):
                is_start = False
            else:
                return "Неверная команда!"
            print(prepare_event_text("RoboCup", is_start))
        elif command == "pr_ev_l":
            print(prepare_event_list())
        elif command == "add_ev":
            get_event("RoboCup", "test", "##.##.####", "##.##.####", "abcdeab", "test_2")
        elif command == "add_pa":
            get_participant(1270000, "qwe", "rty", "RoboCup", "iop", "test", "test_1", "test_2", "##.##.####")
        elif command == "add_se":
            get_info_about_message(7357, "mf_test")
        elif command == "p_p":
            print(print_participants())
        elif command == "p_e":
            print(print_events())
        elif command == "check":
            check_tables()
        elif command == "/exit":
            return "Тест функций прошёл успешно!"
        else:
            return "Неверная команда!"


if __name__ == '__main__':
    print(test())
