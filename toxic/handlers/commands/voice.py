import telegram
from loguru import logger

from toxic.handlers.handler import CommandHandler
from toxic.messenger.message import VoiceMessage
from toxic.messenger.messenger import Messenger
from toxic.repositories.messages import MessagesRepository


class VoiceCommand(CommandHandler):
    def __init__(self, messages_repository: MessagesRepository, messenger: Messenger):
        self.messages_repository = messages_repository
        self.messenger = messenger

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        if message.reply_to_message is None:
            self.messenger.reply(message, 'Нет.')
            return

        # TODO: use message.reply_to_message.text ?

        text_to_voice = self.messages_repository.get_text(message.chat_id, message.reply_to_message.message_id)
        if text_to_voice is None:
            logger.error(
                'Error trying to voice message: message not found.',
                chat_id=message.chat_id,
                reply_to=message.reply_to_message.message_id,
            )
            self.messenger.reply(message, 'Нет.')
            return

        self.messenger.reply(message, VoiceMessage(text_to_voice))
