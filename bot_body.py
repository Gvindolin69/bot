import sqlite3 as sq
import bot_methods as bot
import datetime

# параметры соединения с ДБ и инициация бота токеном
token = '1432164937:AAEuA3Bvoak14-mHXtNdRJupSss_ylqtz00'
journal_bot = bot.Telebot(token)
data = sq.connect('bot_data.db')
cur = data.cursor()
update_id = 0


def main():
    global update_id
    message_is_sanded = False

    while True:
        last_updates = journal_bot.get_first_update()
        cur_id = last_updates['result'][-1]['update_id']

        if cur_id > update_id:
            update_id = cur_id
            message_is_sanded = False
            last_updates = journal_bot.get_updates(update_id)

        message = last_updates['result'][0]['message']
        chat_text = message['text']
        chat_id = message['chat']['id']

        if chat_text == '/start' and not message_is_sanded:
            message_is_sanded = True
            journal_bot.send_message(chat_id, "Это бот для создания журнала с расписанием, чтобы вывести список команд"
                                              "нажмите /help")

        if chat_text == '/help' and not message_is_sanded:
            message_is_sanded = True
            journal_bot.send_help(chat_id)

        if chat_text == '/add_new_user' and not message_is_sanded:
            message_is_sanded = True
            try:
                journal_bot.add_new_user(chat_id)
            except sq.OperationalError:
                journal_bot.send_message(chat_id, "Вы уже есть в базе данных")

        if chat_text == '/add_new_event' and not message_is_sanded:
            event = None

            while event is None:
                if not message_is_sanded and event is None:
                    message_is_sanded = True
                    journal_bot.send_message(chat_id, "Введите название, а затем, через запятую, время и дату в формате"
                                                      " гггг.мм.дд чч:мм")

                elif message_is_sanded and event is None:
                    try:
                        event = (journal_bot.get_updates(update_id + 1)['result'][0]['message']['text']).split(',')
                        message_is_sanded = False
                    except IndexError:
                        print("waiting")
            try:
                event_name = event[0]
                event_date_and_time = datetime.datetime.strptime(event[1], ' %Y.%m.%d %H:%M')
                table_name = "user_" + str(chat_id)
                cur.execute("""INSERT or IGNORE INTO {} VALUES (?, ?, ?)"""
                            .format(table_name), (event_name, str(event_date_and_time.date()), str(event_date_and_time.time())))
                data.commit()
                journal_bot.send_message(chat_id, "Событие успешно добавлено")
            except ValueError:
                journal_bot.send_message(chat_id, "Вы ввели некорректные значения, нажмите"
                                                  " /add_new_event и попробуйте снова")
            except IndexError:
                journal_bot.send_message(chat_id, "Вы ввели некорректные значения, нажмите"
                                                  " /add_new_event и попробуйте снова")

        if chat_text == '/show_my_journal' and not message_is_sanded:
            message_is_sanded = True
            journal_bot.show_user_journal(chat_id)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
