import pandas
import sqlite3
import os

from datetime_EF import get_datetime_now


system = os.name


def _export_to_xlsx():
    try:
        path = "C:\\temp\\" if system == "nt" else "/home/orangepi/tg-bots/temp/"
        try:
            if system == "nt":
                os.mkdir(path)
            elif system == "posix":
                os.system(f"mkdir {path}")
        except OSError:
            pass
        name = ""
        if system == "nt":
            cur_datetime = get_datetime_now().split(".", 2)
            temp = "-".join(cur_datetime)
            cur_datetime = temp.split(":", 2)
            cur_datetime = "-".join(cur_datetime)
            name = f"event_register export {cur_datetime}.xlsx"
        elif system == "posix":
            cur_datetime = get_datetime_now().split(".", 2)
            cur_datetime = "-".join(cur_datetime)
            cur_datetime = cur_datetime.split(":", 2)
            cur_datetime = "-".join(cur_datetime)
            cur_datetime = cur_datetime.split(", ")
            cur_datetime = "_".join(cur_datetime)
            name = f"export_{cur_datetime}.xlsx"
        connect = sqlite3.connect("event_register.db", check_same_thread=False)
        with pandas.ExcelWriter(path + name) as f:
            for i in ["events", "participants", "questions", "sent_messages"]:
                data_file = pandas.read_sql(f'SELECT * FROM {i}', connect)
                data_file.to_excel(f, sheet_name=i, na_rep="--")
        return "Успешно!", path + name
    except Exception as e:
        print(e)
        return "Что-то пошло не так!", "error"


def send_file(bot, user_id):
    result, path = _export_to_xlsx()
    bot.send_message(user_id, "<b><u>" + result + "</u></b>", parse_mode='html')
    if path != "error":
        if system == "nt":
            file = open(path, "rb")
            bot.send_document(user_id, file)
            file.close()
            os.remove(f"\"{path}\"")
            folder = path.split("\\")
            folder = folder[0:-1:1]
            folder = "\\".join(folder)
            os.rmdir(f"\"{folder}\"")
        elif system == "posix":
            file = open(path, "rb")
            bot.send_document(user_id, file)
            file.close()
            folder = path.split("/")
            folder = folder[0:-1:1]
            folder = "/".join(folder)
            os.system(f"rm -i -f {path}")
            os.system("rmdir " + folder)


if __name__ == '__main__':
    raise SystemExit("Этот файл не должен запускаться как основной скрипт!")
