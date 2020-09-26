from typing import List

import telegram

from src import db
from src.helpers import general


class ChatsCommand:
    def handle(self, message: telegram.Message, args: List[str]):
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

            general.reply_text(message, '\n'.join(response))
