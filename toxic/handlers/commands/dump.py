import json
import logging

import telegram

from toxic.db import Database
from toxic.handlers.commands.command import Command
from toxic.messenger import Messenger


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
            logging.error('Caught exception when decoding dump.', exc_info=ex)
            self.messenger.reply(message, dump)
