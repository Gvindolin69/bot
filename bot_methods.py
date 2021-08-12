import json
import requests
import sqlite3 as sq
import datetime

class Telebot:
    def __init__(self, token):
        token = token
        self.url = "https://api.telegram.org/bot{}/{}".format(token, "{}")
        self.bot_data = sq.connect("bot_data.db")
        self.cur = self.bot_data.cursor()


    def get_updates(self, offset, timeout=1):
        params = {'timeout': timeout, 'offset': offset}
        updates = requests.post(self.url.format("getUpdates"), data=params)
        updates_data = updates.json()
        return updates_data

    def get_first_update(self):
        updates = requests.get(self.url.format("getUpdates"))
        updates_data = updates.json()
        return updates_data

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        response = requests.get(self.url.format('sendMessage'), data=params)
        return response

    def send_help(self, chat_id):
        list_of_commands = 'Добавить вас в список пользователей: /add_new_user\n' \
                           'Вывести все ваши заметки с датами: /show_my_journal\n' \
                           'Добавить новое событие: /add_new_event'
        params = {'chat_id': chat_id, 'text': list_of_commands}
        response = requests.post(self.url.format('sendMessage'), data=params)
        return response

    def add_new_user(self, chat_id):
        table_name = "user_" + str(chat_id)
        self.cur.execute("""CREATE TABLE {}(
                                event TEXT,
                                date TEXT,
                                time TEXT);""".format(table_name))
        self.bot_data.commit()
        params = {'chat_id': chat_id, 'text': 'Вы успешно добавлены в базу данных'}
        response = requests.post(self.url.format('sendMessage'), data=params)
        return response

    def show_user_journal(self, chat_id):
        table_name = "user_" + str(chat_id)
        self.cur.execute("""SELECT * FROM {}""".format(table_name))
        res = self.cur.fetchall()
        if not res:
            params = {'chat_id': chat_id, 'text': 'Ващ журнал еще пуст'}
            response = requests.post(self.url.format('sendMessage'), data=params)
        else:
            user_journal = ""
            for i in res:
                for j in i:
                    user_journal += j + " "
                user_journal += "\n"
            params = {'chat_id': chat_id, 'text': user_journal}
            response = requests.post(self.url.format('sendMessage'), data=params)
        return response



