"""
Script to run just once to set messages.text/sticker using updates.json.message.sticker.
"""


import json

import telegram

from toxic import db
from toxic.helpers import consts


def load():
    with db.conn, db.conn.cursor() as cur:
        messages_to_update = []

        cur.execute('SELECT tg_id, json FROM updates ORDER BY tg_id')
        for record in cur:
            update_id, dump = record

            try:
                update = telegram.Update.de_json(dump, consts.bot)
                if update.message is None:
                    continue
                if update.message.sticker is None:
                    continue
            except KeyError:
                continue
            except TypeError:
                continue

            print(update_id, '=>', update.message.sticker.file_id, '|', update.message.sticker.emoji)
            messages_to_update.append((update_id, update.message.sticker.file_id, update.message.sticker.emoji))

    with open('stickers.txt', 'w') as f:
        json.dump(messages_to_update, f)


def save():
    with open('stickers.txt') as f:
        messages_to_update = json.load(f)

    with db.conn, db.conn.cursor() as cur:
        for update_id, file_id, emoji in messages_to_update:
            # cur.execute("SELECT tg_id, update_id, text FROM messages WHERE update_id = %s", (update_id,))
            # for record in cur:
            #     tg_id, update_id, text = record
            #     print(update_id, '=>', text)
            cur.execute("UPDATE messages SET text = %s, sticker = %s WHERE update_id = %s", (emoji, file_id, update_id))


def __main__():
    import main  # pylint: disable=import-outside-toplevel

    main.init(['../../config.json'])

    load()
    save()


if __name__ == '__main__':
    __main__()
