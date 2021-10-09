from __future__ import annotations

import random
import re

import telegram

from toxic.db import Database
from toxic.handlers.handler import Handler
from toxic.helpers import decorators
from toxic.messenger import VoiceMessage, Messenger

SORRY_REGEXP = re.compile(r'бот,\s+извинись')


class KeywordsHandler(Handler):
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
    def handle(self, message: telegram.Message) -> bool:
        for key, val in self.map.items():
            if isinstance(key, str) and key not in message.text.lower():
                continue
            if isinstance(key, re.Pattern) and key.search(message.text.lower()) is None:
                continue

            self.messenger.reply(message, val)
            return True

        return False


class PrivateHandler(Handler):
    def __init__(self, replies: list[str], database: Database, messenger: Messenger):
        self.replies = replies
        self.database = database
        self.messenger = messenger

    def handle(self, message: telegram.Message):
        if self.database.is_admin(message.chat_id):
            self.messenger.reply(message, 'Я запущен', with_delay=False)
        else:
            self.messenger.reply(message, random.choice(self.replies))
        return True


class VoiceHandler(Handler):
    def __init__(self, replies: list[VoiceMessage], messenger: Messenger):
        self.replies = replies
        self.messenger = messenger

    @staticmethod
    def new(config: list[str], messenger: Messenger) -> VoiceHandler:
        replies = []

        for reply in config:
            replies.append(VoiceMessage(reply))

        return VoiceHandler(replies, messenger)

    def handle(self, message: telegram.Message) -> bool:
        # TODO: come up about something funnier
        if message.voice is None and message.video_note is None:
            return False

        self.messenger.reply(message, random.choice(self.replies))
        return True


class SorryHandler(Handler):
    def __init__(self, reply_sorry: str, reply_not_sorry: str, messenger: Messenger):
        self.reply_sorry = reply_sorry
        self.reply_not_sorry = reply_not_sorry
        self.messenger = messenger

    @staticmethod
    def new(config: dict[str, str], messenger: Messenger) -> SorryHandler:
        return SorryHandler(config['sorry'], config['not_sorry'], messenger)

    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            self.messenger.send(message.chat_id, self.reply_not_sorry)
            return True

        if SORRY_REGEXP.search(message.text.lower()) is not None:
            self.messenger.send(message.chat_id, self.reply_sorry)
            return True

        if self.messenger.is_reply_or_mention(message) and 'извинись' in message.text.lower():
            self.messenger.send(message.chat_id, self.reply_sorry)
            return True

        return False
