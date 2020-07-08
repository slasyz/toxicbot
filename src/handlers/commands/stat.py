import telegram

from src import db


class StatCommand:
    def handle(self, message: telegram.Message, args):
        if message.chat_id > 0:
            message.reply_text('Это нужно делать в общем чате, дурачок.')
            return

        with db.conn, db.conn.cursor() as cur:
            cur.execute('''
                SELECT concat(u.first_name, ' ', u.last_name), count(m.tg_id) as c
                FROM messages m
                    JOIN users u on m.user_id = u.tg_id
                WHERE chat_id=%s
                GROUP BY user_id, u.first_name, u.last_name
                ORDER BY c DESC
                LIMIT 10;
            ''', (message.chat_id,))

            response = 'Кто сколько написал с момента запуска бота:\n'
            for record in cur:
                response += f'\n{record[0]} — {record[1]} сообщ.'

            message.reply_text(response)
