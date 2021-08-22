import telegram

from toxic.db import Database
from toxic.handlers.commands.command import Command
from toxic.messenger import Messenger


class ChatsCommand(Command):
    def __init__(self, database: Database, messenger: Messenger):
        self.database = database
        self.messenger = messenger

    def handle(self, message: telegram.Message, args: list[str]):
        rows = self.database.query('''
            SELECT c.tg_id, c.title
            FROM chats c
            WHERE c.tg_id < 0
            UNION
            SELECT u.tg_id, btrim(concat(u.first_name, ' ', u.last_name))
            FROM users u
        ''')

        response = []

        for row in rows:
            response.append(f'{row[1]} — {row[0]}')

        self.messenger.reply(message, '\n'.join(response))
