from __future__ import annotations

from datetime import datetime
from typing import Optional

import telegram

from toxic.db import Database
from toxic.features.chain.featurizer import Featurizer
from toxic.features.chain.textizer import Textizer
from toxic.handlers.handler import MessageHandler
from toxic.features.chain.chain import Chain, ChainFactory, MarkovChain
from toxic.features.chain.splitters import SpaceAdjoinSplitter
from toxic.messenger.messenger import Messenger
from toxic.repositories.chats import CachedChatsRepository


class ChainHandler(MessageHandler):
    def __init__(self, chain_factory: ChainFactory, textizer: Textizer, database: Database, chats_repo: CachedChatsRepository, messenger: Messenger):
        self.chain_factory = chain_factory
        self.textizer = textizer
        self.database = database
        self.chats_repo = chats_repo
        self.messenger = messenger
        self.chats: dict[int, Chain] = {}

    @staticmethod
    def new(chain_factory: ChainFactory, textizer: Textizer, database: Database, chats_repo: CachedChatsRepository, messenger: Messenger) -> ChainHandler:
        chain_handler = ChainHandler(chain_factory, textizer, database, chats_repo, messenger)

        for row in database.query('''
                SELECT chat_id, text 
                FROM messages 
                WHERE chat_id < 0 AND update_id IS NOT NULL 
                ORDER BY tg_id'''):
            chain_handler._teach(row[0], row[1])

        return chain_handler

    def _get_period(self, chat_id: int):
        return self.database.query_row('''SELECT chain_period FROM chats WHERE tg_id = %s''', (chat_id,))[0]

    def _teach(self, chat_id: int, text: Optional[str]):
        chat_id = self.chats_repo.get_latest_chat_id(chat_id)
        try:
            chain = self.chats[chat_id]
        except KeyError:
            chain = self.chain_factory.create()
            self.chats[chat_id] = chain

        self.textizer.teach(chain, text)

    def pre_handle(self, message: telegram.Message):
        if message.chat_id > 0:
            return

        self._teach(message.chat_id, message.text)

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


def __main__():
    import main  # pylint: disable=import-outside-toplevel
    _, database, chats_repo, messenger, metrics, _ = main.init(['../../config.json'])

    # splitter = NoPunctuationSplitter()
    # splitter = PunctuationSplitter()
    splitter = SpaceAdjoinSplitter()
    textizer = Textizer(Featurizer(), splitter, metrics)
    chain_factory = ChainFactory(window=2)
    handler = ChainHandler.new(chain_factory, textizer, database, chats_repo, messenger)

    print(splitter.split("Hello, I'm a string!!! слово ещё,,, а-за-за"))
    # print(handler.chats[-362750796].data)

    for x in range(20):  # pylint: disable=unused-variable
        chain = handler.chats[-362750796]
        print('[' + textizer.predict_not_empty(chain, '') + ']')


if __name__ == '__main__':
    __main__()
