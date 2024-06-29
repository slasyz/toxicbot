from __future__ import annotations

import asyncio
from datetime import datetime

import aiogram
from loguru import logger

from toxic.db import Database
from toxic.interfaces import MessageHandler
from toxic.modules.neural.chains.featurizer import Featurizer
from toxic.modules.neural.chains.textizer import Textizer
from toxic.modules.neural.chains.chain import Chain, ChainFactory
from toxic.modules.neural.chains.splitters import SpaceAdjoinSplitter
from toxic.messenger.message import Message, TextMessage
from toxic.messenger.messenger import Messenger
from toxic.repositories.chats import CachedChatsRepository


class ChainTeachingHandler(MessageHandler):
    def __init__(self, chain_factory: ChainFactory, textizer: Textizer, chats_repo: CachedChatsRepository, chats: dict[int, Chain]):
        self.chain_factory = chain_factory
        self.textizer = textizer
        self.chats_repo = chats_repo
        self.chats = chats

    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        if message.chat.id > 0:
            return None

        await self.teach(message.chat.id, text)
        return None

    async def teach(self, chat_id: int, text: str):
        chat_id = await self.chats_repo.get_latest_chat_id(chat_id)
        try:
            chain = self.chats[chat_id]
        except KeyError:
            chain = self.chain_factory.create()
            self.chats[chat_id] = chain

        self.textizer.teach(chain, text)


class ChainFloodHandler(MessageHandler):
    def __init__(self, textizer: Textizer, database: Database, messenger: Messenger, chats: dict[int, Chain]):
        self.textizer = textizer
        self.database = database
        self.messenger = messenger
        self.chats = chats

    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        if message.chat.id > 0:
            return None

        if await self.messenger.is_reply_or_mention(message):
            chain = self.chats[message.chat.id]
            return [TextMessage(
                self.textizer.predict_not_empty(chain, text),
                with_delay=True,
            )]

        if message.date.timestamp() < datetime.utcnow().timestamp() - 60:
            return None

        count = (await self.database.query_row('SELECT count(tg_id) FROM messages WHERE chat_id = $1', (message.chat.id,)))[0]
        period = (await self.database.query_row('SELECT chain_period FROM chats WHERE tg_id = $1', (message.chat.id,)))[0]
        if count % period == 0:
            chain = self.chats[message.chat.id]
            return [TextMessage(
                self.textizer.predict_not_empty(chain, message.text),
                with_delay=True,
            )]

        return None


async def new(chain_factory: ChainFactory, textizer: Textizer, database: Database, chats_repo: CachedChatsRepository, messenger: Messenger) -> tuple[ChainTeachingHandler, ChainFloodHandler]:
    chats: dict[int, Chain] = {}
    chain_teaching_handler = ChainTeachingHandler(chain_factory, textizer, chats_repo, chats)
    chain_flood_handler = ChainFloodHandler(textizer, database, messenger, chats)

    logger.info('Starting teaching messages.')
    start = datetime.now()
    texts = await database.query('''
        SELECT chat_id, text 
        FROM messages 
        WHERE chat_id < 0 AND update_id IS NOT NULL 
        ORDER BY tg_id
    ''')
    for chat_id, text in texts:
        if text is None:
            continue
        await chain_teaching_handler.teach(chat_id, text)
    logger.info('Finished teaching messages.', duration=str(datetime.now()-start))

    return chain_teaching_handler, chain_flood_handler


async def __main__():
    import main  # pylint: disable=import-outside-toplevel
    deps = await main.init(['../../config.json'])

    # splitter = NoPunctuationSplitter()
    # splitter = PunctuationSplitter()
    splitter = SpaceAdjoinSplitter()
    textizer = Textizer(Featurizer(), splitter, deps.metrics)
    chain_factory = ChainFactory(window=2)
    teaching_handler, _ = await new(chain_factory, textizer, deps.database, deps.chats_repo, deps.messenger)

    print(splitter.split("Hello, I'm a string!!! слово ещё,,, а-за-за"))
    # print(handler.chats[-362750796].data)

    for x in range(20):  # pylint: disable=unused-variable
        chain = teaching_handler.chats[-362750796]
        print('[' + textizer.predict_not_empty(chain, '') + ']')


if __name__ == '__main__':
    asyncio.run(__main__())
