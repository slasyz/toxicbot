import telegram

from toxicbot import db
from toxicbot.handlers.commands.command import Command
from toxicbot.helpers import messages


class ChatsCommand(Command):
    def handle(self, message: telegram.Message, args: list[str]):
        with db.conn, db.conn.cursor() as cur:
            response = []

            cur.execute('''
                SELECT c.tg_id, c.title
                FROM chats c
                WHERE c.tg_id < 0
                UNION
                SELECT u.tg_id, btrim(concat(u.first_name, ' ', u.last_name))
                FROM users u
            ''')
            for record in cur:
                response.append(f'{record[1]} — {record[0]}')

            messages.reply(message, '\n'.join(response))
