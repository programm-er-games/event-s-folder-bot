eng_alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
                "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
                "w", "x", "y", "z"]


def check_email_format(checkstring: str) -> str:
    """
        Returns True, if email from message complies with the standards, else False
    """
    # this variable is intended to check the email for the presence of elements required by the standard
    for i in checkstring:
        if i.lower() not in eng_alphabet and not i.isdigit() and i not in ["@", "_", "."]:
            return "error"
    check_list = {
        "email_name": "",
        "email_sep": "",
        "domain_2": "",
        "address_sep": "",
        "domain_1": ""
    }
    st_1 = checkstring.split("@")
    if len(st_1) == 2:
        check_list["email_name"] = st_1[0]
        check_list["email_sep"] = "@"
    else:
        return "error"
    st_2 = st_1[1].split(".")
    if len(st_2) == 2:
        check_list["domain_2"] = st_2[0]
        check_list["domain_1"] = st_2[1]
        check_list["address_sep"] = "."
    else:
        return "error"
    for i in check_list.keys():
        if check_list[i] == "":
            return "error"
    return checkstring


def check_birth_date_format(checkstring: str) -> str:
    from datetime import datetime
    current_year = datetime.now().year
    temp = checkstring.split(".")
    try:
        # day, month, year = 0, 0, 0
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


def check_integer_format(checkstring: str) -> str: return checkstring if checkstring.isdigit() else "error"


def check_phone_format(checkstring: str) -> str:
    temp = checkstring.split("-")
    is_all_right = True
    is_number = False
    is_plus_detected = False
    for i in temp[0]:
        if i == "+" and temp[0].index(i) == 0:
            is_plus_detected = True
            continue
        if i != " " and i != "-":
            try:
                int(i)
            except ValueError:
                is_number = False
            else:
                is_number = True
        is_all_right = True if is_number and is_plus_detected else False
        if not is_all_right:
            break
    if len(temp[1]) == 2 and len(temp[2]) == 2 and is_all_right:
        try:
            int(temp[1])
            int(temp[2])
        except ValueError:
            is_all_right = False
        else:
            is_all_right = True
    result = checkstring if is_all_right else "error"
    return result


def check_initials_format(checkstring: str) -> str:
    check = checkstring.split(" ")
    return checkstring if len(check) in [2, 3] else "error"


def check_event_info_format(to_check: str) -> dict[str, str] | str:
    result: dict[str, str] = {"": ""}
    del result[""]
    if "\n" in to_check:
        rows = to_check.split("\n")
        counter = 0
        for i in ["name", "description", "date_start", "date_end", "contacts", "address"]:
            temp = rows[counter].split(":")
            if len(temp) > 1:
                try:
                    result[i] = temp[1][1:] if temp[1].startswith(" ") else temp[1]
                except IndexError as e:
                    print(e)
                    return "error"
    return result


if __name__ == '__main__':
    # print(check_birth_date_format("30 12 2005") + " - должно быть неверно")
    # print(check_birth_date_format("32.12.2005") + " - должно быть верно, но нет")
    # print(check_birth_date_format("31.13.2005") + " - должно быть верно, но нет")
    # print(check_birth_date_format("31.12.10000") + " - должно быть верно, но нет")
    # print(check_birth_date_format("10.12.2004") + " - должно быть всё верно")
    # print(check_email_format("e") + " - должно быть неверно")
    # print(check_email_format("@") + " - должно быть неверно")
    # print(check_email_format("ert@") + " - должно быть неверно")
    # print(check_email_format("ert@.d.s") + " - должно быть неверно")
    # print(check_email_format("ert@d.d") + " - должно быть верно")
    raise SystemExit("Этот файл не должен запускаться как основной скрипт!")
