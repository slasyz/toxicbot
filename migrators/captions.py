"""
Script to run just once to set messages.text using updates.dump.caption.
"""


import gzip
import json

import yaml

import main
from src import db


def load():
    with db.conn, db.conn.cursor() as cur:
        messages_to_update = []

        cur.execute('SELECT tg_id, dump FROM updates ORDER BY tg_id')
        for record in cur:
            update_id, dump = record
            update = gzip.decompress(dump.tobytes())
            update = yaml.load(update.decode('utf-8'), yaml.Loader)

            try:
                message = update['message']
                caption = message['caption']

                if caption is None or caption == '':
                    continue
            except KeyError:
                continue
            except TypeError:
                continue

            print(update_id, '=>', caption)
            messages_to_update.append((update_id, caption))

    with open('dump.txt', 'w') as f:
        json.dump(messages_to_update, f)


def save():
    with open('dump.txt') as f:
        messages_to_update = json.load(f)

    with db.conn, db.conn.cursor() as cur:
        for update_id, caption in messages_to_update:
            # cur.execute("SELECT tg_id, update_id, text FROM messages WHERE update_id = %s", (update_id,))
            # for record in cur:
            #     tg_id, update_id, text = record
            #     print(update_id, '=>', text)
            cur.execute("UPDATE messages SET text = %s WHERE update_id = %s AND (text = '' OR text IS NULL)", (caption, update_id))


def __main__():
    main.init()

    load()
    save()


if __name__ == '__main__':
    __main__()
