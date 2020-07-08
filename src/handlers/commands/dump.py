import gzip
import json
import logging
import traceback

import telegram
import yaml

from src import db


class DumpCommand:
    def handle(self, message: telegram.Message, args):
        if len(args) != 2:
            message.reply_text(f'Нужно писать так: /{args[0]} UPDATE_ID')
            return

        try:
            update_id = int(args[1])
        except ValueError:
            message.reply_text(f'Нужно писать так: /{args[0]} UPDATE_ID')
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
                    message.reply_text(json.dumps(json.loads(dump_clean), indent=2, ensure_ascii=False))
                except json.decoder.JSONDecodeError as e:
                    logging.error(str(e) + '\n\n' + traceback.format_exc())
                    message.reply_text(dump_clean)
            else:
                message.reply_text('В базе нет такого апдейта.')
