from __future__ import annotations

from datetime import datetime

import telegram

from toxic.features.chain.featurizer import Featurizer
from toxic.features.chain.textizer import Textizer
from toxic.handlers.handler import MessageHandler
from toxic.features.chain.chain import Chain, ChainFactory
from toxic.features.chain.splitters import SpaceAdjoinSplitter
from toxic.messenger.message import Message, TextMessage
from toxic.messenger.messenger import Messenger
from toxic.repositories.chats import CachedChatsRepository
from toxic.repositories.messages import MessagesRepository


class ChainTeachingHandler(MessageHandler):
    def __init__(self, chain_factory: ChainFactory, textizer: Textizer, chats_repo: CachedChatsRepository, messages_repo: MessagesRepository, messenger: Messenger):
        self.chain_factory = chain_factory
        self.textizer = textizer
        self.chats_repo = chats_repo
        self.chats: dict[int, Chain] = {}

    async def handle(self, text: str, message: telegram.Message) -> str | list[Message] | None:
        if message.chat_id > 0:
            return None

        self.teach(message.chat_id, text)
        return None

    def teach(self, chat_id: int, text: str):
        chat_id = self.chats_repo.get_latest_chat_id(chat_id)
        try:
            chain = self.chats[chat_id]
        except KeyError:
            chain = self.chain_factory.create()
            self.chats[chat_id] = chain

        self.textizer.teach(chain, text)


class ChainFloodHandler(MessageHandler):
    def __init__(self, textizer: Textizer, chats_repo: CachedChatsRepository, messenger: Messenger):
        self.textizer = textizer
        self.chats_repo = chats_repo
        self.messenger = messenger
        self.chats: dict[int, Chain] = {}

    async def handle(self, text: str, message: telegram.Message) -> str | list[Message] | None:
        if message.chat_id > 0:
            return None

        if self.messenger.is_reply_or_mention(message):
            chain = self.chats[message.chat_id]
            return [TextMessage(
                self.textizer.predict_not_empty(chain, text),
                with_delay=True,
            )]

        if message.date.timestamp() < datetime.utcnow().timestamp() - 60:
            return None

        count = self.chats_repo.count_messages(message.chat_id)
        if count % self.chats_repo.get_period(message.chat_id) == 0:
            chain = self.chats[message.chat_id]
            return [TextMessage(
                self.textizer.predict_not_empty(chain, message.text),
                with_delay=True,
            )]

        return None


def new(chain_factory: ChainFactory, textizer: Textizer, chats_repo: CachedChatsRepository, messages_repo: MessagesRepository, messenger: Messenger) -> tuple[ChainTeachingHandler, ChainFloodHandler]:
    chain_teaching_handler = ChainTeachingHandler(chain_factory, textizer, chats_repo, messages_repo, messenger)
    chain_flood_handler = ChainFloodHandler(textizer, chats_repo, messenger)

    # for chat_id, text in messages_repo.get_all_groups_messages():
    #     if text is None:
    #         continue
    #     chain_teaching_handler.teach(chat_id, text)

    return chain_teaching_handler, chain_flood_handler


def __main__():
    import main  # pylint: disable=import-outside-toplevel
    deps = main.init(['../../config.json'])

    # splitter = NoPunctuationSplitter()
    # splitter = PunctuationSplitter()
    splitter = SpaceAdjoinSplitter()
    textizer = Textizer(Featurizer(), splitter, deps.metrics)
    chain_factory = ChainFactory(window=2)
    teaching_handler, _ = new(chain_factory, textizer, deps.chats_repo, deps.messages_repo, deps.messenger)

    print(splitter.split("Hello, I'm a string!!! слово ещё,,, а-за-за"))
    # print(handler.chats[-362750796].data)

    for x in range(20):  # pylint: disable=unused-variable
        chain = teaching_handler.chats[-362750796]
        print('[' + textizer.predict_not_empty(chain, '') + ']')


if __name__ == '__main__':
    __main__()
