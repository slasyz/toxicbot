import sys

import flask
from flask import Flask, render_template

from toxic.db import Database
from toxic.workers.worker import Worker
from toxic.workers.server.models import Group, User, GroupMessage, UserMessage


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

    def _handler_chats(self):
        groups_dict = {}
        users_dict = {}

        # Получаем чаты
        rows = self.database.query('''
            SELECT c.tg_id, c.title, count(m)
            FROM chats c
                LEFT JOIN messages m ON c.tg_id = m.chat_id
            WHERE c.tg_id < 0
            GROUP BY c.tg_id, c.title
            ORDER BY c.title
        ''')
        for row in rows:
            groups_dict[row[0]] = Group(row[0], row[1], row[2])

        # Получаем пользователей
        rows = self.database.query('''
            SELECT u.tg_id, btrim(concat(u.first_name, ' ', u.last_name)) as name, count(m)
            FROM users u
                LEFT JOIN messages m on u.tg_id = m.chat_id
            GROUP BY u.tg_id, u.first_name, u.last_name
            ORDER BY name
        ''')
        for row in rows:
            users_dict[row[0]] = User(row[0], row[1], row[2])

        groups_list = []
        for val in groups_dict.values():
            groups_list.append(val)
        users_list = []
        for val in users_dict.values():
            users_list.append(val)

        return render_template('chats.html', **{
            'groups': groups_list,
            'users': users_list,
        })

    def _handler_group(self, id: int):
        # Получаем чат
        row = self.database.query_row('''
            SELECT c.title, count(m)
            FROM chats c
                LEFT JOIN messages m ON c.tg_id = m.chat_id
            WHERE c.tg_id = %s
            GROUP BY c.tg_id, c.title
        ''', (id,))
        group = Group(id, row[0], row[1])

        messages = []

        # Получаем все сообщения из чата
        rows = self.database.query('''
            SELECT update_id, m.tg_id, user_id, btrim(concat(u.first_name, ' ', u.last_name)), date, text
            FROM messages m
                JOIN users u ON m.user_id = u.tg_id
            WHERE chat_id = %s
            ORDER BY tg_id NULLS FIRST, json_id, update_id
        ''', (id,))
        for row in rows:
            update_id, tg_id, user_id, user_name, date, text = row

            if not text:
                text = ''

            date = date.astimezone(tz=None)

            message = GroupMessage(update_id, tg_id, user_id, user_name, date, text)
            messages.append(message)

        return render_template('group.html', **{
            'group': group,
            'messages': messages,
        })

    def _handler_user(self, id: int):
        # Получаем пользователя
        row = self.database.query_row('''
            SELECT btrim(concat(u.first_name, ' ', u.last_name)), count(m)
            FROM users u
                LEFT JOIN messages m ON u.tg_id = m.chat_id 
            WHERE u.tg_id = %s
            GROUP BY u.tg_id, u.first_name, u.last_name
        ''', (id,))
        user = User(id, row[0], row[1])

        messages = []

        # Получаем все сообщения от пользователя
        rows = self.database.query('''
            SELECT chat_id, update_id, tg_id, date, text
            FROM messages m
            WHERE chat_id = %s
            ORDER BY tg_id NULLS FIRST, json_id, update_id
        ''', (id,))
        for row in rows:
            user_id, update_id, tg_id, date, text = row

            if not text:
                text = ''

            date = date.astimezone(tz=None)

            message = UserMessage(update_id, tg_id, user_id, date, text)
            messages.append(message)

        return render_template('user.html', **{
            'user': user,
            'messages': messages,
        })

    def handler_messages(self):
        id = flask.request.args.get('chat', 0, type=int)
        if id == 0:
            return self._handler_chats()
        if id < 0:
            return self._handler_group(id)
        return self._handler_user(id)


class ServerWorker(Worker):
    def __init__(self, server: Server):
        self.server = server

    def work(self):
        self.server.run()
