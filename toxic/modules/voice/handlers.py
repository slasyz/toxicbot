import aiogram
from loguru import logger

from toxic.db import Database
from toxic.interfaces import CommandHandler
from toxic.messenger.message import VoiceMessage, Message


class VoiceCommand(CommandHandler):
    def __init__(self, database: Database):
        self.database = database

    async def _get_text(self, chat_id: int, message_id: int) -> str | None:
        row = await self.database.query_row('SELECT text FROM messages WHERE chat_id=$1 AND tg_id=$2', (chat_id, message_id))
        if row is None:
            return None

        return row[0]

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        if message.reply_to_message is None:
            return 'Нет.'

        # TODO: use message.reply_to_message.text ?

        text_to_voice = await self._get_text(message.chat.id, message.reply_to_message.message_id)
        if text_to_voice is None:
            logger.error(
                'Error trying to voice message: message not found.',
                chat_id=message.chat.id,
                reply_to=message.reply_to_message.message_id,
            )
            return 'Нет.'

        return [VoiceMessage(text_to_voice)]
