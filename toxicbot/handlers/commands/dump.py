import json
import logging
import traceback

import telegram

from toxicbot.db import Database
from toxicbot.handlers.commands.command import Command
from toxicbot.helpers.messages import Bot


class DumpCommand(Command):
    def __init__(self, database: Database, bot: Bot):
        self.database = database
        self.bot = bot

    def handle(self, message: telegram.Message, args: list[str]):
        if len(args) != 2:
            self.bot.reply(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        try:
            update_id = int(args[1])
        except ValueError:
            self.bot.reply(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        row = self.database.query_row('SELECT json FROM updates WHERE tg_id=%s', (update_id,))
        if row is None:
            self.bot.reply(message, 'В базе нет такого апдейта.')
            return

        dump = row[0]
        try:
            self.bot.reply(message, json.dumps(json.loads(dump), indent=2, ensure_ascii=False))
        except json.decoder.JSONDecodeError as ex:
            logging.error('caught exception %s:\n\n%s', ex, traceback.format_exc())
            self.bot.reply(message, dump)
