import sys
import threading

import jinja2
from flask import Flask, render_template

from src import config, db

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
app = Flask(__name__, template_folder='../../html')


class Chat:
    def __init__(self, id, messages):
        self.id = id
        self.messages = messages
        self.name = 'todo'


class Message:
    def __init__(self, update_id, tg_id, user_id, user_name, date, text):
        self.update_id = update_id
        self.tg_id = tg_id
        self.user_id = user_id
        self.user_name = user_name
        self.date = date
        self.text = text


@app.route('/messages')
def handler_messages():
    with db.conn, db.conn.cursor() as cur:
        chats_dict = {}

        cur.execute('''
            SELECT chat_id, update_id, m.tg_id, user_id, u.first_name, u.last_name, u.username, date, text
            FROM messages m
                JOIN users u on m.user_id = u.tg_id
            ORDER BY tg_id, update_id
        ''')
        for row in cur.fetchall():
            chat_id, update_id, tg_id, user_id, first_name, last_name, username, date, text = row

            text = jinja2.Markup(jinja2.escape(text).replace('\n', '<br>'))  # TODO: не работает

            message = Message(update_id, tg_id, user_id, (first_name or '') + ' ' + (last_name or ''), date, text)
            if chat_id in chats_dict:
                chats_dict[chat_id].messages.append(message)
            else:
                chats_dict[chat_id] = Chat(chat_id, [message])

        chats_list = []
        for key, val in chats_dict.items():
            chats_list.append(val)

        return render_template('messages.html', **{
            'chats': chats_list,
        })


def listen():
    server_config = config.c['server']
    if server_config is not None:
        threading.Thread(target=app.run, kwargs={
            'port': server_config['port'],
        }).start()
