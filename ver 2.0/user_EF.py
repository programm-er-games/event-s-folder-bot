# TODO: добавить ветку админа
# TODO: добавить проверку на повторное прохождение бота:
#  если один и тот же пользователь запускает бота, то предлагать другие варианты событий
#  (
#  хочет ли он изменить данные на запись,
#  хочет ли он записаться на другое/ещё одно мероприятие,
#  хочет ли он отменить заявку на мероприятие/(я)
#  )
from sql_EF import *
from datetime_EF import get_datetime_now


class User:
    def __init__(self, user_id: str, username: str):
        try:
            int(user_id)
        except ValueError:
            raise SystemExit("Неверно задан id пользователя!")
        self._stage = 0
        self._event = ""
        self._event_list_id = 0
        self._current_question = {
            "question": "",
            "type": "",
            "name": ""
        }
        self._is_need_to_check = False
        self._user_info = {
            "id": user_id,
            "username": username,
            "name": "",
            "surname": "",
            "patronymic": ""
        }
        self._qst_counter = 0
        self._qst_number = 0
        self._is_initials = False

    def next_stage(self, to: int = -2):
        if to == -2:
            self._stage += 1
        else:
            self._stage = to

    def _get_qst_number(self):
        if self._event != "":
            self._qst_number = len(search_cond("questions", ["id"], event=self._event))
        else:
            print("Event excepted")

    def set_event(self, event: str):
        self._event = event
        if self._event != "":
            self._get_qst_number()

    def set_list_id(self, event_list_id: int):
        self._event_list_id = event_list_id

    def set_answer(self, answer: str):
        if self._is_initials:
            initials = answer.split(" ")
            self._user_info["name"] = initials[0]
            self._user_info["surname"] = initials[1]
            self._user_info["patronymic"] = initials[2]
            self._is_initials = False
        else:
            self._user_info[self._current_question["name"]] = answer
        # clear question's data
        for i in ["question", "type", "name"]:
            self._current_question[i] = ""

    def set_temp_value(self, key: str, value: Any):
        if "temp" not in self._user_info.keys():
            self._user_info["temp"] = {}
        self._user_info["temp"][key] = value

    def get_temp_value(self, key: str) -> Any | bool:
        if key in self._user_info["temp"].keys():
            return self._user_info["temp"][key]
        else:
            return False

    def get_question(self) -> str:
        self._qst_counter += 1
        if self._qst_counter <= self._qst_number:
            qst = search_cond("questions", ["question", "output_type", "output_name"],
                              event=self._event, id=self._qst_counter)
            if len(qst[0]) != 0:
                self._current_question["question"] = qst[0][0]
                self._current_question["type"] = qst[0][1]
                self._is_initials = True if qst[0][1] == "initials" else False
                self._is_need_to_check = False if qst[0][1] == "text" or qst[0][1] == "integer" else True
                self._current_question["name"] = qst[0][2]
        else:
            return "end"
        # print(self._current_question)
        return self._current_question["question"]

    def is_being_checked(self) -> bool:
        return True if self._current_question["type"] != "text" else False

    def get_stage(self) -> int:
        return self._stage

    def get_event(self) -> str:
        return self._event

    def get_id(self) -> str:
        return self._user_info["id"]

    def get_list_id(self) -> int:
        return self._event_list_id

    def add_user_to_db(self):
        other_info = ""
        if "temp" in self._user_info.keys():
            del self._user_info["temp"]
        keys = self._user_info.keys()
        keys = list(keys)[5:]
        for i in keys:
            other_info += i + " = " + str(self._user_info[i]) + ";\n "
        other_info = other_info[0:-2]
        insert("participants",
               id=int(self._user_info["id"]),
               username=self._user_info["username"],
               name=self._user_info["name"],
               surname=self._user_info["surname"],
               patronymic=self._user_info["patronymic"],
               other_info=other_info,
               event=self._event,
               add_date=get_datetime_now())
