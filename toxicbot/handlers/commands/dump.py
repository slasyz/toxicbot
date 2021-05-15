import json
import logging
import traceback

import telegram

from toxicbot.db import Database
from toxicbot.handlers.commands.command import Command
from toxicbot.messenger import Messenger


class DumpCommand(Command):
    def __init__(self, database: Database, messenger: Messenger):
        self.database = database
        self.messenger = messenger

    def handle(self, message: telegram.Message, args: list[str]):
        if len(args) != 2:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        try:
            update_id = int(args[1])
        except ValueError:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        row = self.database.query_row('SELECT json FROM updates WHERE tg_id=%s', (update_id,))
        if row is None:
            self.messenger.reply(message, 'В базе нет такого апдейта.')
            return

        dump = row[0]
        try:
            self.messenger.reply(message, json.dumps(json.loads(dump), indent=2, ensure_ascii=False))
        except json.decoder.JSONDecodeError as ex:
            logging.error('caught exception %s:\n\n%s', ex, traceback.format_exc())
            self.messenger.reply(message, dump)
