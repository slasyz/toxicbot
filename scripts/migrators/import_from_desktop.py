import asyncio
from datetime import datetime
import json

from toxic.config import Config
from toxic.db import Database


def crop_text(s: str) -> str:
    if len(s) <= 15:
        return s

    return s[:15] + "..."


def handle_text(s) -> str:
    if isinstance(s, str):
        return s
    if isinstance(s, list):
        return ''.join(handle_text(x) for x in s)
    if isinstance(s, dict):
        return s['text']
    raise Exception('Unknown type: {}.'.format(s))


def get_user_id(message: dict) -> int:
    try:
        from_id = message['from_id']
    except KeyError:
        raise Exception('No from_id in message: {}.'.format(message))

    if from_id.startswith('user'):
        return int(from_id[4:])

    raise Exception('Unknown from_id: {}.'.format(from_id))


def get_date(message: dict) -> str:
    date = message['date']
    datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')  # validating
    return date + '+03'


def get_json_id(message: dict) -> int:
    return message['id']


def search_message(database: Database, chat_id: int, user_id: int, s: str, date: str) -> int | None:
    rows = list(database.query(
        'SELECT tg_id FROM messages WHERE chat_id=%s AND user_id=%s AND text=%s AND abs(EXTRACT(epoch from date-%s)) < 1;',
        (chat_id, user_id, s, date),
    ))

    if len(rows) == 0:
        return None

    if len(rows) > 1:
        print('found several candidates for user_id={} date={} text={}'.format(user_id, date, crop_text(s)))

    return rows[0][0]


async def insert(database: Database, chat_id: int, json_id: int, user_id: int, text: str, date: str):
    await database.exec(
        """
        INSERT INTO messages(chat_id, tg_id, json_id, user_id, update_id, text, date, sticker)
        VALUES(%s, NULL, %s, %s, NULL, %s, %s, NULL)
        """,
        (chat_id, json_id, user_id, text, date),
    )


async def update(database: Database, chat_id: int, tg_id: int, json_id: int, text: str):
    await database.exec(
        'UPDATE messages SET json_id = %s WHERE chat_id = %s AND tg_id = %s',
        (json_id, chat_id, tg_id),
    )


async def __main__():
    config = Config.load(['/etc/toxic/config.json'])

    database = await Database.connect(
        config['database']['host'],
        config['database']['port'],
        config['database']['name'],
        config['database']['user'],
        config['database']['pass'],
    )

    # Firstly do this:
    #   jq ".chats.list[] | select(.id == 362750796)" result.json > chat_chatov.json
    chat_id = -362750796

    filename = '/Users/slasyz/Downloads/Telegram Desktop/DataExport_2021-10-01 (1)/chat_chatov.json'

    with open(filename) as f:
        data = json.load(f)

        n = len(data['messages'])

        for i, message in enumerate(data['messages']):
            if message['type'] in ('service',):
                continue

            text = handle_text(message['text'])
            user_id = get_user_id(message)
            date = get_date(message)
            json_id = get_json_id(message)

            tg_id = search_message(database, chat_id, user_id, text, date)
            if tg_id is not None:
                print('{} / {}: setting json_id={} to tg_id={} text={}'.format(i, n, json_id, tg_id, crop_text(text)))
                await update(database, chat_id, tg_id, json_id, text)
            elif text != '':
                print('{} / {}: inserting json_id={} text={}'.format(i, n, json_id, crop_text(text)))
                await insert(database, chat_id, json_id, user_id, text, date)


if __name__ == '__main__':
    asyncio.run(__main__())
