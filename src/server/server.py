import sys
import threading

import jinja2
from flask import Flask, render_template

from src import config, db

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
app = Flask(__name__, template_folder='../../html')


class Chat:
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.messages = []


class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.messages = []


class ChatMessage:
    def __init__(self, update_id, tg_id, user_id, user_name, date, text):
        self.update_id = update_id
        self.tg_id = tg_id
        self.user_id = user_id
        self.user_name = user_name
        self.date = date
        self.text = text


class UserMessage:
    def __init__(self, update_id, tg_id, user_id, date, text):
        self.update_id = update_id
        self.tg_id = tg_id
        self.user_id = user_id
        self.date = date
        self.text = text


@app.route('/messages')
def handler_messages():
    with db.conn, db.conn.cursor() as cur:
        chats_dict = {}
        users_dict = {}

        # Получаем чаты
        cur.execute('''
            SELECT c.tg_id, c.title
            FROM chats c
            WHERE c.tg_id < 0
        ''')
        for record in cur:
            chats_dict[record[0]] = Chat(record[0], record[1])

        # Получаем пользователей
        cur.execute('''
            SELECT u.tg_id, btrim(concat(u.first_name, ' ', u.last_name))
            FROM users u
        ''')
        for record in cur:
            users_dict[record[0]] = User(record[0], record[1])

        # Получаем все сообщения из чатов
        cur.execute('''
            SELECT chat_id, update_id, m.tg_id, user_id, btrim(concat(u.first_name, ' ', u.last_name)), date, text
            FROM messages m
                JOIN users u on m.user_id = u.tg_id
            WHERE chat_id < 0
            ORDER BY tg_id, update_id
        ''')
        for row in cur:
            chat_id, update_id, tg_id, user_id, user_name, date, text = row

            if text:
                text = jinja2.Markup(jinja2.escape(text).replace('\n', '<br>'))  # TODO: не работает
            else:
                text = ''

            date = date.astimezone(tz=None)

            message = ChatMessage(update_id, tg_id, user_id, user_name, date, text)
            chats_dict[chat_id].messages.append(message)

        # Получаем все сообщения от пользователей
        cur.execute('''
            SELECT chat_id, update_id, tg_id, date, text
            FROM messages m
            WHERE chat_id > 0
            ORDER BY tg_id, update_id
        ''')
        for row in cur:
            user_id, update_id, tg_id, date, text = row

            if text:
                text = jinja2.Markup(jinja2.escape(text).replace('\n', '<br>'))  # TODO: не работает
            else:
                text = ''

            date = date.astimezone(tz=None)

            message = UserMessage(update_id, tg_id, user_id, date, text)
            users_dict[user_id].messages.append(message)

        chats_list = []
        for key, val in chats_dict.items():
            chats_list.append(val)
        users_list = []
        for key, val in users_dict.items():
            users_list.append(val)

        return render_template('messages.html', **{
            'chats': chats_list,
            'users': users_list,
        })


def listen():
    server_config = config.c['server']
    if server_config is not None:
        threading.Thread(target=app.run, kwargs={
            'port': server_config['port'],
        }).start()
