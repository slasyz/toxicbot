import re
from typing import List

import telegram

from src import db
from src.helpers import general


class SendCommand:
    def handle(self, message: telegram.Message, args: List[str]):
        if len(args) < 3:
            general.reply_text(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        try:
            chat_id = int(args[1])
        except ValueError:
            general.reply_text(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        with db.conn, db.conn.cursor() as cur:
            cur.execute('SELECT tg_id FROM chats WHERE tg_id=%s', (chat_id,))
            if cur.fetchone() is None:
                general.reply_text(message, f'Не могу найти такой чат ({chat_id}).')
                return

        text = re.sub(r'^/' + args[0] + r'\s+' + args[1] + r'\s+', '', message.text)
        general.send_message(chat_id, text)
