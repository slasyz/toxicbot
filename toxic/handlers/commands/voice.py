import telegram
from loguru import logger

from toxic.handlers.handler import CommandHandler
from toxic.messenger.message import VoiceMessage, Message
from toxic.repositories.messages import MessagesRepository


class VoiceCommand(CommandHandler):
    def __init__(self, messages_repository: MessagesRepository):
        self.messages_repository = messages_repository

    async def handle(self, text: str, message: telegram.Message, args: list[str]) -> str | list[Message] | None:
        if message.reply_to_message is None:
            return 'Нет.'

        # TODO: use message.reply_to_message.text ?

        text_to_voice = self.messages_repository.get_text(message.chat_id, message.reply_to_message.message_id)
        if text_to_voice is None:
            logger.error(
                'Error trying to voice message: message not found.',
                chat_id=message.chat_id,
                reply_to=message.reply_to_message.message_id,
            )
            return 'Нет.'

        return [VoiceMessage(text_to_voice)]
