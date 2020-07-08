import telegram

from src import db
from src.helpers import is_admin


class StatCommand:
    def _get_response(self, chat_id) -> str:
        with db.conn, db.conn.cursor() as cur:
            cur.execute('''
                SELECT btrim(concat(u.first_name, ' ', u.last_name)), count(m.tg_id) as c
                FROM messages m
                    JOIN users u on m.user_id = u.tg_id
                WHERE chat_id=%s
                GROUP BY user_id, u.first_name, u.last_name
                ORDER BY c DESC
                LIMIT 10;
            ''', (chat_id,))

            response = 'Кто сколько написал с момента запуска бота:\n'
            for record in cur:
                response += f'\n{record[0]} — {record[1]} сообщ.'

            return response

    def handle(self, message: telegram.Message, args):
        if message.chat_id < 0:
            response = self._get_response(message.chat_id)
            message.reply_text(response)
            return

        if not is_admin(message.from_user.id):
            message.reply_text('Это нужно делать в общем чате, дурачок.')
            return

        if len(args) != 2:
            message.reply_text(f'Нужно писать так: /{args[0]} CHAT_ID')
            return

        try:
            chat_id = int(args[1])
        except ValueError:
            message.reply_text(f'Нужно писать так: /{args[0]} CHAT_ID')
            return

        response = self._get_response(chat_id)
        message.reply_text(response)
