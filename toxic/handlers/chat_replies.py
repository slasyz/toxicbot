from __future__ import annotations

import random
import re

import telegram

from toxic.handlers.handler import MessageHandler
from toxic.helpers import decorators
from toxic.messenger.messenger import Messenger
from toxic.repositories.users import UsersRepository

SORRY_REGEXP = re.compile(r'бот,\s+извинись')


class KeywordsHandler(MessageHandler):
    def __init__(self, map: dict[re.Pattern, str], messenger: Messenger):
        self.map = map
        self.messenger = messenger

    @staticmethod
    def new(config: dict[str, str], messenger: Messenger) -> KeywordsHandler:
        map = {}

        for key, val in config.items():
            regexp = re.compile(key)
            map[regexp] = val

        return KeywordsHandler(map, messenger)

    @decorators.non_empty
    def handle(self, text: str, message: telegram.Message) -> bool:
        # pylint: disable=W0221
        # Because of the decorator
        for key, val in self.map.items():
            if isinstance(key, str) and key not in text.lower():
                continue
            if isinstance(key, re.Pattern) and key.search(text.lower()) is None:
                continue

            self.messenger.reply(message, val)
            return True

        return False


class PrivateHandler(MessageHandler):
    def __init__(self, replies: list[str], users_repo: UsersRepository, messenger: Messenger):
        self.replies = replies
        self.users_repo = users_repo
        self.messenger = messenger

    def handle(self, message: telegram.Message):
        if self.users_repo.is_admin(message.chat_id):
            self.messenger.reply(message, 'Я запущен')
        else:
            self.messenger.reply(message, random.choice(self.replies))
        return True


class SorryHandler(MessageHandler):
    def __init__(self, reply_sorry: str, reply_not_sorry: str, messenger: Messenger):
        self.reply_sorry = reply_sorry
        self.reply_not_sorry = reply_not_sorry
        self.messenger = messenger

    @staticmethod
    def new(config: dict[str, str], messenger: Messenger) -> SorryHandler:
        return SorryHandler(config['sorry'], config['not_sorry'], messenger)

    @decorators.non_empty
    def handle(self, text: str, message: telegram.Message) -> bool:
        # pylint: disable=W0221
        # Because of the decorator
        if message.chat_id > 0:
            self.messenger.send(message.chat_id, self.reply_not_sorry)
            return True

        if SORRY_REGEXP.search(text.lower()) is not None:
            self.messenger.send(message.chat_id, self.reply_sorry)
            return True

        if self.messenger.is_reply_or_mention(message) and 'извинись' in text.lower():
            self.messenger.send(message.chat_id, self.reply_sorry)
            return True

        return False
