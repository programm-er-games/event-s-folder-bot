# TODO: добавить модульность и гибкость программе
from EF import bot, queue_manager
from sql_EF import check_tables
from datetime_EF import get_datetime_now


@bot.message_handler(content_types=['text'])
def main(message):
    queue_manager(message)


if __name__ == "__main__":
    check_tables()
    print(f"Starting \"Event's folder v2.0\" bot...\n{get_datetime_now()}")
    bot.polling(skip_pending=True)
