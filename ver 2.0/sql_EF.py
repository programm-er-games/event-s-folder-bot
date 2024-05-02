# TODO: добавить модульность и гибкость программе
# TODO: фича: делать отдельные таблицы для отдельных мероприятий
import sqlite3
from typing import Any

conn = sqlite3.Connection("event_register.db", check_same_thread=False)
cur = conn.cursor()


def check_tables():
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
            username     TEXT UNIQUE
                              NOT NULL,
            name         TEXT NOT NULL,
            surname      TEXT NOT NULL,
            patronymic   TEXT,
            event        TEXT NOT NULL,
            other_info   TEXT NOT NULL,
            add_date     TEXT NOT NULL
        )""")
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS sent_messages (
            id             INTEGER NOT NULL,
            message_text   TEXT,
            datetime TEXT    NOT NULL
        )""")
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS questions (
            event           TEXT     NOT NULL,
            id              INTEGER  NOT NULL,
            question        TEXT     NOT NULL,
            output_type     TEXT     NOT NULL,
            output_name     TEXT     NOT NULL
        )""")
    conn.commit()


def insert(table: str, **kwargs):
    rq = "INSERT INTO " + table + " ("
    for i in kwargs.keys():
        rq += i + ", "
    rq = rq[0:-2]
    rq += ") VALUES ("
    for i in kwargs:
        if isinstance(kwargs[i], str):
            rq += "\"" + kwargs[i] + "\", "
        else:
            rq += str(kwargs[i]) + ", "
    rq = rq[0:-2]
    rq += ")"
    cur.execute(rq)
    conn.commit()


def search_all(table: str, *args: str):
    rq = "SELECT "
    for i in args:
        rq += i + ", "
    rq = rq[0:-2]
    rq += " FROM " + table
    result = cur.execute(rq).fetchall()
    conn.commit()
    return result


def search_cond(table: str, columns: list, **kwargs):
    rq = "SELECT "
    for i in columns:
        rq += i + ", "
    rq = rq[0:-2]
    rq += " FROM " + table + " WHERE "
    for i in kwargs.keys():
        rq += i
        if isinstance(kwargs[i], str):
            rq += "=\"" + kwargs[i] + "\" AND "
        else:
            rq += "=" + str(kwargs[i]) + " AND "
    rq = rq[0:-5]
    result = cur.execute(rq).fetchall()
    conn.commit()
    return result


def update(table: str, columns: dict[str, Any], **kwargs):
    rq = "UPDATE " + table + " SET "
    for i in columns.keys():
        rq += i
        if isinstance(columns[i], str):
            rq += " = \"" + kwargs[i] + "\", "
        else:
            rq += " = " + str(kwargs[i]) + ", "
    rq = rq[0:-2]
    rq += " WHERE "
    for i in kwargs.keys():
        rq += i
        if isinstance(kwargs[i], str):
            rq += "=\"" + kwargs[i] + "\" AND "
        else:
            rq += "=" + str(kwargs[i]) + " AND "
    rq = rq[0:-5]
    cur.execute(rq)
    conn.commit()


def delete(table: str, **kwargs):
    rq = "DELETE FROM " + table + " WHERE "
    for i in kwargs.keys():
        rq += i
        if isinstance(kwargs[i], str):
            rq += "=\"" + kwargs[i] + "\" AND "
        else:
            rq += "=" + str(kwargs[i]) + " AND "
    rq = rq[0:-5]
    cur.execute(rq)
    conn.commit()

# def test():
#     print(", ".join(["name", "fgh"]))


if __name__ == '__main__':
    # test()
    raise SystemError("Этот файл не должен запускаться как основной скрипт!")
