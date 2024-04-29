eng_alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
                "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
                "w", "x", "y", "z"]


def check_email_format(checkstring: str):
    """
        Returns True, if email from message complies with the standards, else False
    """
    is_dog_detected = False
    is_dot_detected = False  # переменная для обозначения наличия точки после наличия собаки
    is_all_right = False
    for symbol in checkstring:
        if symbol in eng_alphabet or \
                symbol.lower() in eng_alphabet or \
                symbol == ".":
            is_all_right = True
        elif symbol == "@":
            is_dog_detected = True
        else:
            is_all_right = False
        if symbol == "." and is_dog_detected:
            is_dot_detected = True
        if not is_all_right:
            break
    if is_all_right and is_dog_detected and is_dot_detected:
        return checkstring
    else:
        return "error"


def check_birth_date_format(checkstring: str):
    from datetime import datetime
    current_year = datetime.now().year
    temp = checkstring.split(".")
    try:
        day, month, year = 0, 0, 0
        if len(temp) == 3:
            day = int(temp[0])
            month = int(temp[1])
            year = int(temp[2])
        else:
            return "error"
        if (not (0 <= day <= 31)
                or not (0 <= month <= 12)
                or not ((1800 <= year <= 9999) and year < current_year)):
            return "correct, but error"
        else:
            # if current_year - year >= 5:
            return checkstring
    except Exception as e:
        print(e)
        return "error"


if __name__ == '__main__':
    print(check_birth_date_format("30 12 2005") + " - должно быть неверно")
    print(check_birth_date_format("32.12.2005") + " - должно быть верно, но нет")
    print(check_birth_date_format("31.13.2005") + " - должно быть верно, но нет")
    print(check_birth_date_format("31.12.10000") + " - должно быть верно, но нет")
    print(check_birth_date_format("10.12.2004") + " - должно быть всё верно")
    raise SystemExit("Этот файл не должен запускаться как основной скрипт!")

