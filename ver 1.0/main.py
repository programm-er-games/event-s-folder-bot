from EF import manager, bot, finish_session

# переменная, которая будет хранить в себе id пользователя, который начал работу с ботом
start_id: int = 0
# переменная, которая будет хранить в себе id пользователей, которые будут начинать работу с ботом
queue_id: list = []
# переменная для обозначения окончания работы пользователя с ботом
is_finished: bool = False


@bot.message_handler(content_types=['text'])
def main(message):
    """
        Here we immediately check if the user is writing to us.
        If yes, then we run the distributing function,
        otherwise we send a message that this user cannot use the bot yet
    """
    if message.from_user.id == start_id or start_id == 0:
        queue_manager(message)
    else:
        bot.send_message(message.from_user.id,
                              "Вы находитесь в очереди, поэтому <b>Вы не можете начать работу с ботом</b>.\n"
                              "Мы пришлём Вам сообщение, "
                              "как только другой пользователь закончит работу с ним",
                              parse_mode="html")


def queue_manager(message):
    """
        This feature adds users to the queue to use the bot. Returns True, if user has finished with bot, else False
    """
    global start_id, queue_id, is_finished
    for i in queue_id:
        print(str(queue_id.index(i, 0, int(queue_id.__sizeof__() / 4))) + ", " + str(i) + "; ")
    # если никто ещё не запускал бота, то заполняем переменную id пользователя, который первый начал работу с ботом
    if start_id == 0:
        start_id = message.from_user.id
    # если сообщение пришло от того пользователя, который работает с ботом, то работаем с этим сообщением
    if message.from_user.id == start_id:
        is_finished = manager(message)
    else:
        if start_id != message.from_user.id:
            queue_id.append(message.from_user.id)
    if is_finished:
        finish_session(message)
        if queue_id:
            bot.send_message(queue_id[0], "Теперь <b>Вы</b> можете начать работу с ботом!", parse_mode='html')
            start_id = queue_id[0]
            del queue_id[0]


if __name__ == "__main__":
    raise SystemExit("Эта версия выведена из строя в связи с переходом на новую версию.\n"
                     "Данная версия имеет некоторые критические баги и ошибки, которые надо "
                     "было исправить перед внезапной презентацией бота, "
                     "а времени на них категорически не хватает.\n"
                     "Не рекомендуется использовать!")
    print("Starting \"Event's folder\" bot...")
    from sql_EF import get_datetime_now

    # используем точное время запуска бота для отладки
    print(get_datetime_now())
    bot.polling(non_stop=True, timeout=5, skip_pending=True)
else:
    raise SystemExit("Это главный исполняемый файл, он должен запускаться первым в порядке")
