import sys

from flask import Flask, render_template

from toxicbot.db import Database
from toxicbot.workers.worker import Worker
from toxicbot.workers.server.models import Chat, User, ChatMessage, UserMessage


class Server:
    def __init__(self, host: str, port: int, database: Database):
        self.host = host
        self.port = port
        self.database = database

    def run(self):
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None
        # TODO: replace with FastAPI?
        app = Flask(__name__, template_folder='../../../html')
        app.route('/messages')(self.handler_messages)
        # TODO: replace app.run() with something production ready; or not
        app.run(host=self.host, port=self.port)

    def handler_messages(self):
        chats_dict = {}
        users_dict = {}

        # Получаем чаты
        rows = self.database.query('''
            SELECT c.tg_id, c.title
            FROM chats c
            WHERE c.tg_id < 0
        ''')
        for row in rows:
            chats_dict[row[0]] = Chat(row[0], row[1])

        # Получаем пользователей
        rows = self.database.query('''
            SELECT u.tg_id, btrim(concat(u.first_name, ' ', u.last_name))
            FROM users u
        ''')
        for row in rows:
            users_dict[row[0]] = User(row[0], row[1])

        # Получаем все сообщения из чатов
        rows = self.database.query('''
            SELECT chat_id, update_id, m.tg_id, user_id, btrim(concat(u.first_name, ' ', u.last_name)), date, text
            FROM messages m
                JOIN users u on m.user_id = u.tg_id
            WHERE chat_id < 0
            ORDER BY tg_id, update_id
        ''')
        for row in rows:
            chat_id, update_id, tg_id, user_id, user_name, date, text = row

            if not text:
                text = ''

            date = date.astimezone(tz=None)

            message = ChatMessage(update_id, tg_id, user_id, user_name, date, text)
            chats_dict[chat_id].messages.append(message)

        # Получаем все сообщения от пользователей
        rows = self.database.query('''
            SELECT chat_id, update_id, tg_id, date, text
            FROM messages m
            WHERE chat_id > 0
            ORDER BY tg_id, update_id
        ''')
        for row in rows:
            user_id, update_id, tg_id, date, text = row

            if not text:
                text = ''

            date = date.astimezone(tz=None)

            message = UserMessage(update_id, tg_id, user_id, date, text)
            users_dict[user_id].messages.append(message)

        chats_list = []
        for val in chats_dict.values():
            chats_list.append(val)
        users_list = []
        for val in users_dict.values():
            users_list.append(val)

        return render_template('messages.html', **{
            'chats': chats_list,
            'users': users_list,
        })


class ServerWorker(Worker):
    def __init__(self, server: Server):
        self.server = server

    def work(self):
        self.server.run()
