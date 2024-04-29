def about(message, bot, markup_remove):
    text = "Данный бот создан замечательным, но скромным человеком Поповым Алексеем Эдуардовичем " \
           "на собственном энтузиазме. По вопросам или предложениям по поводу этого бота " \
           "обращаться к этому боту или человеку (если вдруг бот будет не работать): " \
           "@FeedbackAboutBots_bot или @QuizBot_Developer"
    bot.send_message(message.chat.id, text, reply_markup=markup_remove)
