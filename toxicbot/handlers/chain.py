from datetime import datetime
from typing import Optional

import telegram

from toxicbot import db
from toxicbot.features.chain.featurizer import Featurizer
from toxicbot.features.chain.textizer import Textizer
from toxicbot.handlers.handler import Handler
from toxicbot.helpers import messages
from toxicbot.features.chain.chain import Chain, ChainFactory
from toxicbot.features.chain.splitters import PunctuationSplitter


class ChainHandler(Handler):
    def __init__(self, chain_factory: ChainFactory, textizer: Textizer):
        self.chain_factory = chain_factory
        self.textizer = textizer
        self.chats: dict[int, Chain] = {}

    def _get_period(self, chat_id: int):
        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT chain_period FROM chats WHERE tg_id = %s''', (chat_id,))
            record = cur.fetchone()
            return record[0]

    def teach(self, chat_id: int, text: Optional[str]):
        try:
            chain = self.chats[chat_id]
        except KeyError:
            chain = self.chain_factory.create()
            self.chats[chat_id] = chain

        self.textizer.teach(chain, text)

    def pre_handle(self, message: telegram.Message):
        if message.chat_id > 0:
            return

        self.teach(message.chat_id, message.text)

    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            return False

        if messages.is_reply_or_mention(message):
            chain = self.chats[message.chat_id]
            text = self.textizer.predict_not_empty(chain, message.text)
            messages.reply(message, text)
            return True

        if message.date.timestamp() < datetime.utcnow().timestamp() - 60:
            return False

        with db.conn, db.conn.cursor() as cur:
            cur.execute('''SELECT count(tg_id) FROM messages WHERE chat_id = %s''', (message.chat_id,))
            record = cur.fetchone()
            count = record[0]

            if count % self._get_period(message.chat_id) == 0:
                chain = self.chats[message.chat_id]
                text = self.textizer.predict_not_empty(chain, message.text)
                messages.send(message.chat_id, text)
                return True

        return False


class ChainHandlerFactory:
    def __init__(self, chain_factory: ChainFactory, textizer: Textizer):
        self.chain_factory = chain_factory
        self.textizer = textizer

    def create(self) -> ChainHandler:
        chain_handler = ChainHandler(chain_factory=self.chain_factory, textizer=self.textizer)

        with db.conn, db.conn.cursor() as cur:
            # TODO: игнорировать изменения сообщений
            cur.execute('''
                SELECT chat_id, text 
                FROM messages 
                WHERE chat_id < 0 AND update_id IS NOT NULL 
                ORDER BY tg_id
            ''')
            for record in cur:
                chain_handler.teach(record[0], record[1])

        return chain_handler


def __main__():
    import main  # pylint: disable=import-outside-toplevel
    main.init(['../../config.json'])

    # splitter = NoPunctuationSplitter()
    splitter = PunctuationSplitter()
    textizer = Textizer(Featurizer(), splitter)
    chain_factory = ChainFactory(window=3)
    handler = ChainHandlerFactory(chain_factory, textizer).create()

    print(splitter.split("Hello, I'm a string!!! слово ещё,,, а-за-за"))
    # print(handler.chats[-362750796].data)

    for x in range(20):  # pylint: disable=unused-variable
        chain = handler.chats[-362750796]
        print('[' + textizer.predict_not_empty(chain, '') + ']')


if __name__ == '__main__':
    __main__()
