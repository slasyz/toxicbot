import gzip
import json
import logging
import traceback
from typing import List

import telegram
import yaml

from src import db, helpers


class DumpCommand:
    def handle(self, message: telegram.Message, args: List[str]):
        if len(args) != 2:
            helpers.reply_text(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        try:
            update_id = int(args[1])
        except ValueError:
            helpers.reply_text(message, f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        with db.conn, db.conn.cursor() as cur:
            cur.execute('SELECT dump FROM updates WHERE tg_id=%s', (update_id,))
            res = cur.fetchone()
            if res is not None:
                dump = bytes(res[0])
                dump = gzip.decompress(dump)
                dump = str(yaml.load(dump, Loader=yaml.Loader))
                dump_clean = dump.replace('"', '\\"').replace("'", '"').replace('True', 'true').replace('False',
                                                                                                        'false')

                try:
                    helpers.reply_text(message, json.dumps(json.loads(dump_clean), indent=2, ensure_ascii=False))
                except json.decoder.JSONDecodeError as e:
                    logging.error(str(e) + '\n\n' + traceback.format_exc())
                    helpers.reply_text(message, dump_clean)
            else:
                helpers.reply_text(message, 'В базе нет такого апдейта.')
