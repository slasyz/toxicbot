import telegram

from toxicbot.db import Database
from toxicbot.handlers.commands.command import Command
from toxicbot.messenger import Messenger, VoiceMessage


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
            # TODO: залогировать ошибку нормально
            self.messenger.reply(message, 'Нет (не могу найти {} и {}).'.format(message.chat_id, message.reply_to_message.message_id))
            return

        self.messenger.reply(message, VoiceMessage(row[0]))
