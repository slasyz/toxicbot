import random
import re

import telegram

from toxicbot.handlers.handler import Handler
from toxicbot.helpers import decorators, general, messages
from toxicbot.helpers.messages import VoiceMessage


KEYWORDS = {
    re.compile(r'(иди|пошел|пошла|пошёл)\s+(на\s?хуй|в\s?пизду|в\s?ж[еоё]пп?у)'): 'Что за токсичность...',
    'пидор': 'Пошёл нахуй.',
}


class KeywordsHandler(Handler):
    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        for key, val in KEYWORDS.items():
            if isinstance(key, str) and key not in message.text.lower():
                return False
            if isinstance(key, re.Pattern) and key.search(message.text.lower()) is None:
                return False

            messages.reply(message, val)
            return True


PRIVATE_ANSWERS = [
    'Сделаю вид, что я этого не заметил.',
    'Давай притворимся, будто этого не было.',
    'Щас пожалуюсь Славе, что ты до меня домогаешься.'
]


class PrivateHandler(Handler):
    def handle(self, message: telegram.Message):
        if general.is_admin(message.chat_id):
            messages.reply(message, 'Я запущен')
        else:
            messages.reply(message, random.choice(PRIVATE_ANSWERS))
        return True


VOICE_ANSWERS = [
    VoiceMessage('И что, мы должны щас все бросить свои дела и слушать это?'),
    VoiceMessage('Зумеры совсем обезумели, буквы печатать разучились.'),
    VoiceMessage('Напиши текстом.'),
    VoiceMessage('Кожаный мешок, я не понимаю, что ты говоришь.'),
]

VOICE_DELAY = 2


class VoiceHandler(Handler):
    def handle(self, message: telegram.Message) -> bool:
        if message.voice is None and message.video_note is None:
            return False

        messages.reply(message, random.choice(VOICE_ANSWERS), delay=VOICE_DELAY)
        return True


SORRY_REGEXP = re.compile(r'бот,\s+извинись')


class SorryHandler(Handler):
    @decorators.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            messages.send(message.chat_id, 'Отсоси, потом проси.')
            return True

        if SORRY_REGEXP.search(message.text.lower()) is not None:
            messages.send(message.chat_id, 'Извините.')
            return True

        if messages.is_reply_or_mention(message) and 'извинись' in message.text.lower():
            messages.send(message.chat_id, 'Извините.')
            return True

        return False
