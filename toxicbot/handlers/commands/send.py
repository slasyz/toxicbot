import re

import telegram

from toxicbot.db import Database
from toxicbot.handlers.commands.command import Command
from toxicbot.helpers.messages import Bot


class SendCommand(Command):
    def __init__(self, database: Database, bot: Bot):
        self.database = database
        self.bot = bot

    def handle(self, message: telegram.Message, args: list[str]):
        if len(args) < 3:
            self.bot.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        try:
            chat_id = int(args[1])
        except ValueError:
            self.bot.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        row = self.database.query('SELECT tg_id FROM chats WHERE tg_id=%s', (chat_id,))
        if row is None:
            self.bot.reply(message, f'Не могу найти такой чат ({chat_id}).')
            return

        prefix_regexp = re.compile(r'^/' + args[0] + r'\s+' + args[1] + r'\s+')
        text = prefix_regexp.sub('', message.text)
        self.bot.send(chat_id, text)
