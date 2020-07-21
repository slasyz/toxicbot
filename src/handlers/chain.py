import os
import random
import re
import time
from datetime import datetime
from typing import Union, List

import telegram

from src import db, helpers

BREAK = '[BREAK]'


class Chain:
    def __init__(self, window: int, chat_id: int):
        self.window = window
        self.chat_id = chat_id
        self.data = {}
        self.current = ()

        self.teach_word(BREAK)

    @staticmethod
    def split_words(message: str) -> List[str]:
        return re.split(r'[^\w]+', message)
        # return re.findall(r"[\w'-]+|\s+|[^\w\s'-]+", message)

    @staticmethod
    def pick(stat: dict) -> str:
        res = []
        for key, value in stat.items():
            res += [key] * value

        return random.choice(res)

    def teach_word(self, word: str):
        if len(self.current) == self.window and (self.current[-1] != BREAK or word != BREAK):
            if self.current in self.data:
                if word in self.data[self.current]:
                    self.data[self.current][word] += 1
                else:
                    self.data[self.current][word] = 1
            else:
                self.data[self.current] = {word: 1}

        self.current = self.current[1:] + (word,)

    def teach_message(self, message: Union[str, type(None)]):
        if message is None or message == '':
            return

        regex = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'
        message = re.sub(regex, '', message)
        words = self.split_words(message)
        for word in words:
            if word != '':  # TODO: [картинка]
                self.teach_word(word.lower())
        self.teach_word(BREAK)

    def predict(self, message: str) -> str:
        if self.window == 1:
            current = (BREAK,)
        else:
            arr = re.split(r'[^\w]+', message)  # TODO: если нет достаточного числа слов
            current = tuple(arr[-self.window+1:]) + (BREAK,)

        result = []
        while True:
            try:
                stat = self.data[current]
            except KeyError:
                break

            word = self.pick(stat)
            current = (word,)

            if current == (BREAK,):
                break
            else:
                result.append(word)

        res = ' '.join(result)
        if res != '':
            return res[0].upper() + res[1:]
        else:
            return ''


class ChainHandler:
    def __init__(self):
        self.chats = {}
        self.window = 1

        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT tg_id, chain_period FROM chats''')
            for record in cur:
                self.chats[record[0]] = Chain(self.window, record[0])

            # TODO: игнорировать изменения сообщений
            cur.execute('''SELECT chat_id, text FROM messages WHERE chat_id < 0 ORDER BY tg_id''')
            for record in cur:
                try:
                    chain = self.chats[record[0]]
                except KeyError:
                    chain = Chain(self.window, record[0])
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
            chain = Chain(self.window, message.chat_id)
            self.chats[message.chat_id] = chain

        chain.teach_message(message.text)

    def match(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            return False

        if message.reply_to_message is not None and message.reply_to_message.from_user.id == helpers.bot.id:
            text = self.chats[message.chat_id].predict(message.text)
            message.reply_text(text)
            return True

        for entity in message.entities:
            if entity.type == 'mention' and message.text[entity.offset:entity.offset+entity.length] == '@' + helpers.bot.username:
                text = 'Чё? ' + self.chats[message.chat_id].predict(message.text)
                message.reply_text(text)
                return True

        if message.date.timestamp() < datetime.utcnow().timestamp() - 60:
            return False

        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT count(tg_id) FROM messages WHERE chat_id = %s''', (message.chat_id,))
            record = cur.fetchone()
            count = record[0]

            if count % self._get_period(message.chat_id) == 0:
                text = self.chats[message.chat_id].predict(message.text)
                helpers.bot.send_message(message.chat_id, text)
                return True

        return False

    def handle(self, message: telegram.Message):
        pass


def __main__():
    from src import config, logging

    logging.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()

    config.load('../../config.json')
    db.connect()

    handler = ChainHandler()

    print(Chain.split_words("Hello, I'm a string!!! слово ещё,,, а-за-за"))
    print(handler.chats[-362750796].data)

    for x in range(20):
        print(handler.chats[-362750796].predict(''))


if __name__ == '__main__':
    __main__()
