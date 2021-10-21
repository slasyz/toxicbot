import re

import telegram

from toxic.db import Database
from toxic.handlers.commands.command import Command
from toxic.messenger.messenger import Messenger


class SendCommand(Command):
    def __init__(self, database: Database, messenger: Messenger):
        self.database = database
        self.messenger = messenger

    def handle(self, message: telegram.Message, args: list[str]):
        if len(args) < 3:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        try:
            chat_id = int(args[1])
        except ValueError:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        row = self.database.query('SELECT tg_id FROM chats WHERE tg_id=%s', (chat_id,))
        if row is None:
            self.messenger.reply(message, f'Не могу найти такой чат ({chat_id}).')
            return

        prefix_regexp = re.compile(r'^/' + args[0] + r'\s+' + args[1] + r'\s+')
        text = prefix_regexp.sub('', message.text)
        self.messenger.send(chat_id, text)
