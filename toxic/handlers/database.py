import telegram
from loguru import logger

from toxic.db import Database
from toxic.metrics import Metrics


class DatabaseUpdateSaver:
    def __init__(self, database: Database, metrics: Metrics):
        self.database = database
        self.metrics = metrics

    def handle_user(self, user: telegram.User):
        row = self.database.query_row('''
            SELECT first_name, last_name, username 
            FROM users 
            WHERE tg_id=%s
        ''', (user.id,))

        if row is None:
            self.database.exec('''
                INSERT INTO users(tg_id, first_name, last_name, username)
                VALUES(%s, %s, %s, %s)
            ''', (
                user.id,
                user.first_name,
                user.last_name,
                user.username
            ))
        elif row[0] != user.first_name or row[1] != user.last_name or row[2] != user.username:
            self.database.exec('''
                UPDATE users
                SET first_name = %s,
                    last_name = %s,
                    username = %s
                WHERE tg_id = %s
            ''', (
                user.first_name,
                user.last_name,
                user.username,
                user.id
            ))

    def handle_chat(self, chat: telegram.Chat):
        title = chat.title or (((chat.first_name or '') + ' ' + (chat.last_name or '')).strip()) or None

        row = self.database.query_row('SELECT title FROM chats WHERE tg_id=%s', (chat.id,))
        if row is None:
            self.database.exec('''
                INSERT INTO chats(tg_id, title)
                VALUES(%s, %s)
            ''', (
                chat.id,
                title
            ))
        elif row[0] != title:
            self.database.exec('''
                UPDATE chats
                SET title = %s
                WHERE tg_id=%s
            ''', (
                title,
                chat.id
            ))

    def handle_message(self, message: telegram.Message, update_id: int | None = None):
        if message.from_user is not None:
            self.handle_user(message.from_user)
        if message.chat is not None:
            self.handle_chat(message.chat)

        row = self.database.query_row('SELECT true FROM messages WHERE chat_id=%s AND tg_id=%s AND update_id=%s', (
            message.chat_id,
            message.message_id,
            update_id
        ))
        if row is not None:
            return

        text = ''
        sticker = None
        if message.text is not None:
            text = message.text
        elif message.caption is not None:
            text = message.caption
        elif message.sticker is not None:
            text = message.sticker.emoji or ''
            sticker = message.sticker.file_id

        from_user_id = None
        if message.from_user is not None:
            from_user_id = message.from_user.id

        self.database.exec('''
            INSERT INTO messages(chat_id, tg_id, user_id, update_id, text, date, sticker)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (chat_id, json_id, tg_id) DO UPDATE SET 
                update_id = %s,
                text = %s,
                date = %s,
                sticker = %s
        ''', (
            message.chat_id,
            message.message_id,
            from_user_id,
            update_id,
            text,
            message.date,
            sticker,
            update_id,
            text,
            message.date,
            sticker
        ))

        row = self.database.query_row('''SELECT count(*) FROM messages''')
        self.metrics.messages.set(row[0])

    async def handle(self, update: telegram.Update):
        row = self.database.query_row('SELECT true FROM updates WHERE tg_id=%s', (update.update_id,))
        if row is not None:
            logger.info('Ignoring update #{}.', update.update_id)
            return

        logger.info('Handling update.', **update.to_dict())

        message = update.message or update.edited_message
        chat_id = 0
        if message is not None:
            chat_id = message.chat_id

        self.database.exec('''
            INSERT INTO updates(tg_id, chat_id, json)
            VALUES(%s, %s, %s)
        ''', (
            update.update_id,
            chat_id,
            update.to_json(),
        ))

        if message is None:
            return

        self.handle_message(message, update.update_id)
