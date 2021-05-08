import random
import re

import telegram

from toxicbot.handlers.handler import Handler
from toxicbot.helpers import decorators, general, messages
from toxicbot.helpers.messages import VoiceMessage


SORRY_REGEXP = re.compile(r'бот,\s+извинись')


class KeywordsHandler(Handler):
    def __init__(self, map: dict[re.Pattern, str]):
        self.map = map

    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        for key, val in self.map.items():
            if isinstance(key, str) and key not in message.text.lower():
                continue
            if isinstance(key, re.Pattern) and key.search(message.text.lower()) is None:
                continue

            messages.reply(message, val)
            return True

        return False


class KeywordsHandlerFactory:
    def create(self, config: dict[str, str]) -> KeywordsHandler:
        map = {}

        for key, val in config.items():
            regexp = re.compile(key)
            map[regexp] = val

        return KeywordsHandler(map)


class PrivateHandler(Handler):
    def __init__(self, replies: list[str]):
        self.replies = replies

    def handle(self, message: telegram.Message):
        if general.is_admin(message.chat_id):
            messages.reply(message, 'Я запущен', delay=0)
        else:
            messages.reply(message, random.choice(self.replies))
        return True


class VoiceHandler(Handler):
    def __init__(self, replies: list[VoiceMessage]):
        self.replies = replies

    def handle(self, message: telegram.Message) -> bool:
        if message.voice is None and message.video_note is None:
            return False

        messages.reply(message, random.choice(self.replies))
        return True


class VoiceHandlerFactory:
    def create(self, config: list[str]) -> VoiceHandler:
        replies = []

        for reply in config:
            replies.append(VoiceMessage(reply))

        return VoiceHandler(replies)


class SorryHandler(Handler):
    def __init__(self, reply_sorry: str, reply_not_sorry: str):
        self.reply_sorry = reply_sorry
        self.reply_not_sorry = reply_not_sorry

    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            messages.send(message.chat_id, self.reply_not_sorry)
            return True

        if SORRY_REGEXP.search(message.text.lower()) is not None:
            messages.send(message.chat_id, self.reply_sorry)
            return True

        if messages.is_reply_or_mention(message) and 'извинись' in message.text.lower():
            messages.send(message.chat_id, self.reply_sorry)
            return True

        return False


class SorryHandlerFactory:
    def create(self, config: dict[str, str]) -> SorryHandler:
        return SorryHandler(config['sorry'], config['not_sorry'])
