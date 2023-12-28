import pandas
import sqlite3
import os

from sql_EF import current_datetime


def remove_quotes_from_path(path: str):
    prepared_path = ""
    if path[0] == "\"" and path[len(path) - 1] == "\"":
        for i in path:
            prepared_path += i if i != "\"" else ""
        return prepared_path
    else:
        return path


def is_exists_and_normal(src_path: str, src_name: str, dst_path: str, dst_name: str):  # поменять название функции
    is_file_exist = os.path.exists(src_path + src_name)
    if is_file_exist:
        try:
            os.rename(src_path + src_name, dst_path + dst_name)
        except Exception as e:
            print(e)
            return False
        else:
            return True
    else:
        file = open(dst_path + dst_name, "a+")
        return True


def prepare_name_string(name: str, path: str):
    temp = ""
    is_changed = False
    for i in name:
        temp += "_" if i == "'" else i
        is_changed = True if i == "'" else False
    is_exists_and_normal(path, name, path, temp)
    name = temp if is_changed else name
    name += "" if name.endswith(".xlsx") else ".xlsx"
    result = name if path.endswith("\\") else "\\" + name
    return result


def export_to_xlsx(path="", name=""):

    path = "\\" if path == "" else remove_quotes_from_path(path)
    cur_datetime = current_datetime.split(".", 2)
    temp = "-".join(cur_datetime)
    cur_datetime = temp.split(":", 2)
    cur_datetime = "-".join(cur_datetime)
    name = f"event_register export {cur_datetime}.xlsx" if name == "" else name
    name = prepare_name_string(name, path)
    connect = sqlite3.connect("event_register.db", check_same_thread=False)
    with pandas.ExcelWriter(path + name) as f:
        for i in ["events", "participants", "sent_messages"]:
            data_file = pandas.read_sql(f'SELECT * FROM {i}', connect)
            data_file.to_excel(f, sheet_name=i, na_rep="--")
    return f"Успешно! Файл сохранен в: {path + name}", path + name


if __name__ == '__main__':
    print(export_to_xlsx("C:\\"))
