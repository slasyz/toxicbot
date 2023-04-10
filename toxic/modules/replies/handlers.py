from __future__ import annotations

import random
import re

import aiogram
from loguru import logger

from toxic.helpers import decorators
from toxic.interfaces import MessageHandler
from toxic.messenger.message import Message
from toxic.messenger.messenger import Messenger
from toxic.repositories.messages import MessagesRepository
from toxic.repositories.users import UsersRepository

SORRY_REGEXP = re.compile(r'бот,\s+извинись')


class KeywordsHandler(MessageHandler):
    def __init__(self, map: dict[re.Pattern, list[str]]):
        self.map = map

    @staticmethod
    def new(config: dict[str, str | list[str]]) -> KeywordsHandler:
        map = {}

        for key, val in config.items():
            regexp = re.compile(key)
            if isinstance(val, str):
                val = [val]
            map[regexp] = val

        return KeywordsHandler(map)

    @decorators.non_empty
    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        # pylint: disable=W0221
        # Because of the decorator
        for key, val in self.map.items():
            if isinstance(key, str) and key not in text.lower():
                continue
            if isinstance(key, re.Pattern) and key.search(text.lower()) is None:
                continue

            return random.choice(val)

        return None


class PeopleHandler(MessageHandler):
    def __init__(self, users: dict[int, dict[str, str | list[str]]], mirror_phrases: dict[tuple[int, int], list[str]], messenger: Messenger):
        self.users = users
        self.messenger = messenger
        self.mirror_phrases = mirror_phrases

    @staticmethod
    async def new(users_raw: dict[str, dict[str, str | list[str]]], messenger: Messenger, messages_repo: MessagesRepository) -> PeopleHandler:
        users = {}
        mirror_phrases: dict[tuple[int, int], list[str]] = {}

        for key, val in users_raw.items():
            if isinstance(val, str):
                val = [val]
            users[int(key)] = val

            async for chat_id, text in messages_repo.get_all_user_messages(int(key)):
                if (chat_id, int(key)) not in mirror_phrases:
                    mirror_phrases[(chat_id, int(key))] = []
                logger.info(f'appending mirror to {chat_id} {int(key)}')
                mirror_phrases[(chat_id, int(key))].append(text)

        for key, val in mirror_phrases.items():
            logger.info(f'Mirror phrases: chat = {key[0]}, user = {key[1]}, loaded {len(val)} mirror phrases')

        return PeopleHandler(users, mirror_phrases, messenger)

    @decorators.non_empty
    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        # pylint: disable=W0221
        # Because of the decorator
        if not await self.messenger.is_reply_or_mention(message):
            return None

        if message.from_user.id not in self.users:
            return None

        user_config = self.users[message.from_user.id]
        user_const_phrases = user_config.get('phrases', [])

        user_mirroring_phrases = self.mirror_phrases.get((message.chat.id, message.from_user.id), [])
        if not user_config.get('mirroring', False):
            user_mirroring_phrases = []

        if len(user_mirroring_phrases) == 0 and len(user_const_phrases) == 0:
            return None

        if len(user_mirroring_phrases) == 0:
            return random.choice(user_const_phrases)

        return random.choice(user_mirroring_phrases)


class PrivateHandler(MessageHandler):
    def __init__(self, replies: list[str], users_repo: UsersRepository):
        self.replies = replies
        self.users_repo = users_repo

    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        if message.chat.id < 0:
            return None

        if await self.users_repo.is_admin(message.chat.id):
            return 'Я запущен'

        return random.choice(self.replies)


class SorryHandler(MessageHandler):
    def __init__(self, reply_sorry: str, reply_not_sorry: str, messenger: Messenger):
        self.reply_sorry = reply_sorry
        self.reply_not_sorry = reply_not_sorry
        self.messenger = messenger

    @staticmethod
    def new(config: dict[str, str], messenger: Messenger) -> SorryHandler:
        return SorryHandler(config['sorry'], config['not_sorry'], messenger)

    @decorators.non_empty
    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        # pylint: disable=W0221
        # Because of the decorator
        reply = self.reply_sorry
        if message.chat.id > 0:
            reply = self.reply_not_sorry

        if SORRY_REGEXP.search(text.lower()) is not None:
            return reply

        if await self.messenger.is_reply_or_mention(message) and 'извинись' in text.lower():
            return reply

        return None
