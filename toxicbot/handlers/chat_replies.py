import random
import re

import telegram

from toxicbot.db import Database
from toxicbot.handlers.handler import Handler
from toxicbot.helpers import decorators
from toxicbot.helpers.messages import VoiceMessage, Bot

SORRY_REGEXP = re.compile(r'бот,\s+извинись')


class KeywordsHandler(Handler):
    def __init__(self, map: dict[re.Pattern, str], bot: Bot):
        self.map = map
        self.bot = bot

    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        for key, val in self.map.items():
            if isinstance(key, str) and key not in message.text.lower():
                continue
            if isinstance(key, re.Pattern) and key.search(message.text.lower()) is None:
                continue

            self.bot.reply(message, val)
            return True

        return False


class KeywordsHandlerFactory:
    def create(self, config: dict[str, str], bot: Bot) -> KeywordsHandler:
        map = {}

        for key, val in config.items():
            regexp = re.compile(key)
            map[regexp] = val

        return KeywordsHandler(map, bot)


class PrivateHandler(Handler):
    def __init__(self, replies: list[str], database: Database, bot: Bot):
        self.replies = replies
        self.database = database
        self.bot = bot

    def handle(self, message: telegram.Message):
        if self.database.is_admin(message.chat_id):
            self.bot.reply(message, 'Я запущен', delay=0)
        else:
            self.bot.reply(message, random.choice(self.replies))
        return True


class VoiceHandler(Handler):
    def __init__(self, replies: list[VoiceMessage], bot: Bot):
        self.replies = replies
        self.bot = bot

    def handle(self, message: telegram.Message) -> bool:
        if message.voice is None and message.video_note is None:
            return False

        self.bot.reply(message, random.choice(self.replies))
        return True


class VoiceHandlerFactory:
    def create(self, config: list[str], bot: Bot) -> VoiceHandler:
        replies = []

        for reply in config:
            replies.append(VoiceMessage(reply))

        return VoiceHandler(replies, bot)


class SorryHandler(Handler):
    def __init__(self, reply_sorry: str, reply_not_sorry: str, bot: Bot):
        self.reply_sorry = reply_sorry
        self.reply_not_sorry = reply_not_sorry
        self.bot = bot

    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            self.bot.send(message.chat_id, self.reply_not_sorry)
            return True

        if SORRY_REGEXP.search(message.text.lower()) is not None:
            self.bot.send(message.chat_id, self.reply_sorry)
            return True

        if self.bot.is_reply_or_mention(message) and 'извинись' in message.text.lower():
            self.bot.send(message.chat_id, self.reply_sorry)
            return True

        return False


class SorryHandlerFactory:
    def create(self, config: dict[str, str], bot: Bot) -> SorryHandler:
        return SorryHandler(config['sorry'], config['not_sorry'], bot)
