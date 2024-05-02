from datetime import datetime


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