import re
from typing import List

import telegram

from src import db, helpers


class SendCommand:
    def handle(self, message: telegram.Message, args: List[str]):
        if len(args) < 3:
            message.reply_text(f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        try:
            chat_id = int(args[1])
        except ValueError:
            message.reply_text(f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        with db.conn, db.conn.cursor() as cur:
            cur.execute('SELECT tg_id FROM chats WHERE tg_id=%s', (chat_id,))
            if cur.fetchone() is None:
                message.reply_text(f'Не могу найти такой чат ({chat_id}).')

        text = re.split(r'\s+', message.text, 3)[2]
        helpers.bot.send_message(chat_id, text)
