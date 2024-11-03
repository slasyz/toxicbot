import aiogram
from loguru import logger

from toxic.db import Database
from toxic.interfaces import MessageHandler
from toxic.messenger.message import Message
from toxic.modules.neural.handlers import ChainTeachingHandler


class MigrateHandler(MessageHandler):
    def __init__(self, database: Database, chain_teaching_handler: ChainTeachingHandler):
        self.database = database
        self.chain_teaching_handler = chain_teaching_handler

    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        if message.migrate_to_chat_id is None:
            return None

        # Migrating the chat to new ID in all places where we use its id
        logger.info('Chat migrated.', chat_id=message.chat.id, new_chat_id=message.migrate_to_chat_id)

        await self.database.exec('UPDATE updates SET chat_id = $1 WHERE chat_id = $2', (message.migrate_to_chat_id, message.chat.id))
        await self.database.exec('UPDATE messages SET chat_id = $1 WHERE chat_id = $2', (message.migrate_to_chat_id, message.chat.id))
        await self.database.exec('UPDATE reminders SET chat_id = $1 WHERE chat_id = $2', (message.migrate_to_chat_id, message.chat.id))

        await self.database.exec('UPDATE chats SET chain_period = (SELECT chain_period FROM chats WHERE tg_id = $1) WHERE tg_id = $2', (message.chat.id, message.migrate_to_chat_id))
        await self.database.exec('UPDATE chats SET joke_period = (SELECT joke_period FROM chats WHERE tg_id = $1) WHERE tg_id = $2', (message.chat.id, message.migrate_to_chat_id))
        await self.database.exec('DELETE FROM chats WHERE tg_id = $1', (message.chat.id,))

        self.chain_teaching_handler.migrate_chat(message.chat.id, message.migrate_to_chat_id)

        return None
