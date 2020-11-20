import random
import re

import telegram

from src.handlers.handler import Handler
from src.helpers import decorators, general
from src.helpers.message import VoiceMessage


NAHUY_REGEXP = re.compile(r'(иди|пошел|пошла|пошёл)\s+(на\s?хуй|в\s?пизду|в\s?ж[еоё]пп?у)')
NAHUY_ANSWER = 'Что за токсичность...'


class NahuyHandler(Handler):
    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if NAHUY_REGEXP.search(message.text.lower()) is None:
            return False

        general.reply(message, NAHUY_ANSWER)
        return True


class PidorHandler(Handler):
    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if 'пидор' not in message.text.lower():
            return False

        general.reply(message, 'Пошёл нахуй.')
        return True


PRIVATE_ANSWERS = [
    'Сделаю вид, что я этого не заметил.',
    'Давай притворимся, будто этого не было.',
    'Щас пожалуюсь Славе, что ты до меня домогаешься.'
]


class PrivateHandler(Handler):
    def handle(self, message: telegram.Message):
        if general.is_admin(message.chat_id):
            general.reply(message, 'Я запущен')
        else:
            general.reply(message, random.choice(PRIVATE_ANSWERS))
        return True


VOICE_ANSWERS = [
    VoiceMessage('И что, мы должны щас все бросить свои дела и слушать это?'),
    VoiceMessage('Зумеры совсем обезумели, буквы печатать разучились.'),
    VoiceMessage('Напиши текстом.'),
    VoiceMessage('Кожаный мешок, я не понимаю, что ты говоришь.'),
]


class VoiceHandler(Handler):
    def handle(self, message: telegram.Message) -> bool:
        if message.voice is None and message.video_note is None:
            return False

        general.reply(message, random.choice(VOICE_ANSWERS))
        return True


SORRY_REGEXP = re.compile(r'бот,\s+извинись')


class SorryHandler(Handler):
    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            general.send(message.chat_id, 'Отсоси, потом проси.')
            return True

        if SORRY_REGEXP.search(message.text.lower()) is not None:
            general.send(message.chat_id, 'Извините.')
            return True

        if general.is_reply_or_mention(message) and 'извинись' in message.text.lower():
            general.send(message.chat_id, 'Извините.')
            return True

        return False
