import logging

import telegram

from toxic.db import Database
from toxic.handlers.commands.command import Command
from toxic.messenger.messenger import Messenger, VoiceMessage


class VoiceCommand(Command):
    def __init__(self, database: Database, messenger: Messenger):
        self.database = database
        self.messenger = messenger

    def handle(self, message: telegram.Message, args: list[str]):
        if message.reply_to_message is None:
            self.messenger.reply(message, 'Нет.')
            return

        row = self.database.query_row('SELECT text FROM messages WHERE chat_id=%s AND tg_id=%s', (message.chat_id, message.reply_to_message.message_id))
        if row is None:
            logging.error('Error trying to voice message: message not found.', extra={
                'chat_id': message.chat_id,
                'reply_to': message.reply_to_message.message_id,
            })
            self.messenger.reply(message, 'Нет.')
            return

        self.messenger.reply(message, VoiceMessage(row[0]))
