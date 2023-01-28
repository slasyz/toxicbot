import aiogram
from loguru import logger

from toxic.db import Database
from toxic.metrics import Metrics


class DatabaseUpdateSaver:
    def __init__(self, database: Database, metrics: Metrics):
        self.database = database
        self.metrics = metrics

    async def handle_user(self, user: aiogram.types.User):
        row = await self.database.query_row('''
            SELECT first_name, last_name, username 
            FROM users 
            WHERE tg_id=$1
        ''', (user.id,))

        if row is None:
            await self.database.exec('''
                INSERT INTO users(tg_id, first_name, last_name, username)
                VALUES($1, $2, $3, $4)
            ''', (
                user.id,
                user.first_name,
                user.last_name,
                user.username
            ))
        elif row[0] != user.first_name or row[1] != user.last_name or row[2] != user.username:
            await self.database.exec('''
                UPDATE users
                SET first_name = $1,
                    last_name = $2,
                    username = $3
                WHERE tg_id = $4
            ''', (
                user.first_name,
                user.last_name,
                user.username,
                user.id
            ))

    async def handle_chat(self, chat: aiogram.types.Chat):
        title = chat.title or (((chat.first_name or '') + ' ' + (chat.last_name or '')).strip()) or None

        row = await self.database.query_row('SELECT title FROM chats WHERE tg_id=$1', (chat.id,))
        if row is None:
            await self.database.exec('''
                INSERT INTO chats(tg_id, title)
                VALUES($1, $2)
            ''', (
                chat.id,
                title
            ))
        elif row[0] != title:
            await self.database.exec('''
                UPDATE chats
                SET title = $1
                WHERE tg_id=$2
            ''', (
                title,
                chat.id
            ))

    async def handle_message(self, message: aiogram.types.Message, update_id: int | None = None):
        if message.from_user is not None:
            await self.handle_user(message.from_user)
        if message.chat is not None:
            await self.handle_chat(message.chat)

        row = await self.database.query_row('SELECT true FROM messages WHERE chat_id=$1 AND tg_id=$2 AND update_id=$3', (
            message.chat.id,
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

        await self.database.exec('''
            INSERT INTO messages(chat_id, tg_id, user_id, update_id, text, date, sticker)
            VALUES($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (chat_id, json_id, tg_id) DO UPDATE SET 
                update_id = $8,
                text = $9,
                date = $10,
                sticker = $11
        ''', (
            message.chat.id,
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

        row = await self.database.query_row('''SELECT count(*) FROM messages''')
        self.metrics.messages.set(row[0])

    async def handle(self, update: aiogram.types.Update):
        row = await self.database.query_row('SELECT true FROM updates WHERE tg_id=$1', (update.update_id,))
        if row is not None:
            logger.info('Ignoring update #{}.', update.update_id)
            return

        logger.info('Handling update.', **update.to_python())

        message = update.message or update.edited_message
        chat_id = 0
        if message is not None:
            chat_id = message.chat.id

        await self.database.exec('''
            INSERT INTO updates(tg_id, chat_id, json)
            VALUES($1, $2, $3)
        ''', (
            update.update_id,
            chat_id,
            update.as_json(),
        ))

        if message is None:
            return

        await self.handle_message(message, update.update_id)
