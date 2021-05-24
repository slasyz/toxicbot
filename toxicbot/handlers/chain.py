from datetime import datetime
from typing import Optional

import telegram

from toxicbot.db import Database
from toxicbot.features.chain.featurizer import Featurizer
from toxicbot.features.chain.textizer import Textizer
from toxicbot.handlers.handler import Handler
from toxicbot.features.chain.chain import Chain, ChainFactory
from toxicbot.features.chain.splitters import PunctuationSplitter
from toxicbot.messenger import Messenger


class ChainHandler(Handler):
    def __init__(self, chain_factory: ChainFactory, textizer: Textizer, database: Database, messenger: Messenger):
        self.chain_factory = chain_factory
        self.textizer = textizer
        self.database = database
        self.messenger = messenger
        self.chats: dict[int, Chain] = {}

    def _get_period(self, chat_id: int):
        return self.database.query_row('''SELECT chain_period FROM chats WHERE tg_id = %s''', (chat_id,))[0]

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

        if self.messenger.is_reply_or_mention(message):
            chain = self.chats[message.chat_id]
            text = self.textizer.predict_not_empty(chain, message.text)
            self.messenger.reply(message, text)
            return True

        if message.date.timestamp() < datetime.utcnow().timestamp() - 60:
            return False

        row = self.database.query_row('''SELECT count(tg_id) FROM messages WHERE chat_id = %s''', (message.chat_id,))
        count = row[0]
        if count % self._get_period(message.chat_id) == 0:
            chain = self.chats[message.chat_id]
            text = self.textizer.predict_not_empty(chain, message.text)
            self.messenger.send(message.chat_id, text)
            return True

        return False


class ChainHandlerFactory:
    def __init__(self, chain_factory: ChainFactory, textizer: Textizer, database: Database, messenger: Messenger):
        self.chain_factory = chain_factory
        self.textizer = textizer
        self.database = database
        self.messenger = messenger

    def create(self) -> ChainHandler:
        chain_handler = ChainHandler(self.chain_factory, self.textizer, self.database, self.messenger)

        for row in self.database.query('''
                SELECT chat_id, text 
                FROM messages 
                WHERE chat_id < 0 AND update_id IS NOT NULL 
                ORDER BY tg_id'''):
            chain_handler.teach(row[0], row[1])

        return chain_handler


def __main__():
    import main  # pylint: disable=import-outside-toplevel
    _, database, messenger, metrics, _ = main.init(['../../config.json'])

    # splitter = NoPunctuationSplitter()
    splitter = PunctuationSplitter()
    textizer = Textizer(Featurizer(), splitter, metrics)
    chain_factory = ChainFactory(window=3)
    handler = ChainHandlerFactory(chain_factory, textizer, database, messenger).create()

    print(splitter.split("Hello, I'm a string!!! слово ещё,,, а-за-за"))
    # print(handler.chats[-362750796].data)

    for x in range(20):  # pylint: disable=unused-variable
        chain = handler.chats[-362750796]
        print('[' + textizer.predict_not_empty(chain, '') + ']')


if __name__ == '__main__':
    __main__()
