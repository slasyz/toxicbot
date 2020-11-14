import os
import time
from datetime import datetime

import telegram

from src import db
from src.helpers import general
from src.services.chain.chain import Chain
from src.services.chain.splitters import Splitter, NoPunctuationSplitter


class ChainHandler:
    def __init__(self, window: int, splitter: Splitter):
        self.chats = {}
        self.window = window
        self.splitter = splitter

        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT tg_id, chain_period FROM chats''')
            for record in cur:
                self.chats[record[0]] = Chain(self.window, self.splitter)

            # TODO: игнорировать изменения сообщений
            cur.execute('''
                SELECT chat_id, text 
                FROM messages 
                WHERE chat_id < 0 AND update_id IS NOT NULL 
                ORDER BY tg_id
            ''')
            for record in cur:
                try:
                    chain = self.chats[record[0]]
                except KeyError:
                    chain = Chain(self.window, self.splitter)
                    self.chats[record[0]] = chain
                chain.teach_message(record[1])

    def _get_period(self, chat_id: int):
        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT chain_period FROM chats WHERE tg_id = %s''', (chat_id,))
            record = cur.fetchone()
            return record[0]

    def pre_handle(self, message: telegram.Message):
        if message.chat_id > 0:
            return

        try:
            chain = self.chats[message.chat_id]
        except KeyError:
            chain = Chain(self.window, self.splitter)
            self.chats[message.chat_id] = chain

        chain.teach_message(message.text)

    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            return False

        if general.is_reply_or_mention(message):
            text = self.chats[message.chat_id].predict(message.text)
            general.reply_text(message, text)
            return True

        if message.date.timestamp() < datetime.utcnow().timestamp() - 60:
            return False

        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT count(tg_id) FROM messages WHERE chat_id = %s''', (message.chat_id,))
            record = cur.fetchone()
            count = record[0]

            if count % self._get_period(message.chat_id) == 0:
                text = self.chats[message.chat_id].predict(message.text)
                general.send_message(message.chat_id, text)
                return True

        return False


def __main__():
    from src import config  # pylint: disable=import-outside-toplevel
    from src.helpers import logging  # pylint: disable=import-outside-toplevel

    logging.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()

    config.load('../../config.json')
    db.connect()

    splitter = NoPunctuationSplitter()
    handler = ChainHandler(window=1, splitter=splitter)

    print(splitter.split_tokens("Hello, I'm a string!!! слово ещё,,, а-за-за"))
    # print(handler.chats[-362750796].data)

    for x in range(20):    # pylint: disable=unused-variable
        print(handler.chats[-362750796].predict(''))


if __name__ == '__main__':
    __main__()
