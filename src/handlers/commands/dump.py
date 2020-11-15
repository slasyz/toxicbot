import json
import logging
import traceback
from typing import List

import telegram

from src import db
from src.handlers.commands.command import Command
from src.helpers import general


class DumpCommand(Command):
    def handle(self, message: telegram.Message, args: List[str]):
        if len(args) != 2:
            general.reply(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        try:
            update_id = int(args[1])
        except ValueError:
            general.reply(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        with db.conn, db.conn.cursor() as cur:
            cur.execute('SELECT json FROM updates WHERE tg_id=%s', (update_id,))
            res = cur.fetchone()
            if res is None:
                general.reply(message, 'В базе нет такого апдейта.')
                return

            try:
                general.reply(message, json.dumps(json.loads(res[0]), indent=2, ensure_ascii=False))
            except json.decoder.JSONDecodeError as e:
                logging.error('caught exception %s:\n\n%s', e, traceback.format_exc())
                general.reply(message, res[0])
