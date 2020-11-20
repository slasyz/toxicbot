import re
from typing import List

import telegram

from src import db
from src.handlers.commands.command import Command
from src.helpers import messages


class SendCommand(Command):
    def handle(self, message: telegram.Message, args: List[str]):
        if len(args) < 3:
            messages.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        try:
            chat_id = int(args[1])
        except ValueError:
            messages.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        with db.conn, db.conn.cursor() as cur:
            cur.execute('SELECT tg_id FROM chats WHERE tg_id=%s', (chat_id,))
            if cur.fetchone() is None:
                messages.reply(message, f'Не могу найти такой чат ({chat_id}).')
                return

        prefix_regexp = re.compile(r'^/' + args[0] + r'\s+' + args[1] + r'\s+')
        text = prefix_regexp.sub('', message.text)
        messages.send(chat_id, text)
