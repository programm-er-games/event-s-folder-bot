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
    result = ""
    try:
        day = int(temp[0])
        month = int(temp[1])
        year = int(temp[2])
        if not(0 <= day <= 31):
            result = "correct, but error"
        elif not(0 <= month <= 12):
            result = "correct, but error"
        if (1800 <= year <= 9999) and year < current_year:
            if current_year - year >= 5:
                result = checkstring
        else:
            result = "correct, but error"
    except ValueError:
        result = "error"
    finally:
        return result
