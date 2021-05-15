import telegram

from toxicbot.db import Database
from toxicbot.handlers.commands.command import Command
from toxicbot.helpers.messages import Bot


class ChatsCommand(Command):
    def __init__(self, database: Database, bot: Bot):
        self.database = database
        self.bot = bot

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

        self.bot.reply(message, '\n'.join(response))
