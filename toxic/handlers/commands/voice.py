import logging

import telegram

from toxic.handlers.commands.command import Command
from toxic.messenger.message import VoiceMessage
from toxic.messenger.messenger import Messenger
from toxic.repositories.messages import MessagesRepository


class VoiceCommand(Command):
    def __init__(self, messages_repository: MessagesRepository, messenger: Messenger):
        self.messages_repository = messages_repository
        self.messenger = messenger

    def handle(self, message: telegram.Message, args: list[str]):
        if message.reply_to_message is None:
            self.messenger.reply(message, 'Нет.')
            return

        # TODO: use message.reply_to_message.text ?

        text = self.messages_repository.get_text(message.chat_id, message.reply_to_message.message_id)
        if text is None:
            logging.error('Error trying to voice message: message not found.', extra={
                'chat_id': message.chat_id,
                'reply_to': message.reply_to_message.message_id,
            })
            self.messenger.reply(message, 'Нет.')
            return

        self.messenger.reply(message, VoiceMessage(text))
