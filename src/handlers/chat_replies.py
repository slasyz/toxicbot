import random
import re

import telegram

from src import helpers
from src.helpers import non_empty, is_admin

NAHUY_REGEXP = r'(иди|пошел|пошла|пошёл)\s+(на\s?хуй|в\s?пизду|в\s?ж[еоё]пп?у)'
NAHUY_ANSWER = 'Что за токсичность...'


class NahuyHandler:
    @non_empty
    def match(self, message: telegram.Message) -> bool:
        return re.search(NAHUY_REGEXP, message.text.lower()) is not None

    def handle(self, message: telegram.Message):
        message.reply_text(NAHUY_ANSWER)


class PidorHandler:
    @non_empty
    def match(self, message: telegram.Message) -> bool:
        return 'пидор' in message.text.lower()

    def handle(self, message: telegram.Message):
        message.reply_text('Пошёл нахуй.')


PRIVATE_ANSWERS = [
    'Сделаю вид, что я этого не заметил.',
    'Давай притворимся, будто этого не было.',
    'Щас пожалуюсь Славе, что ты до меня домогаешься.'
]


class PrivateHandler:
    def match(self, message: telegram.Message) -> bool:
        return True

    def handle(self, message: telegram.Message):
        if is_admin(message.chat_id):
            message.reply_text('Я запущен')
        else:
            message.reply_text(random.choice(PRIVATE_ANSWERS))


VOICE_ANSWERS = [
    'И что, мы должны щас все бросить свои дела и слушать это?',
    'Зумеры совсем обезумели, буквы печатать разучились.',
    'Напиши текстом.',
    'Бляяя...',
]


class VoiceHandler:
    def match(self, message: telegram.Message) -> bool:
        return message.voice is not None or message.video_note is not None

    def handle(self, message: telegram.Message):
        message.reply_text(random.choice(VOICE_ANSWERS))


class MentionHandler:
    def match(self, message: telegram.Message) -> bool:
        for entity in message.entities:
            if entity.type == 'mention' and message.text[entity.offset:entity.offset+entity.length] == '@' + helpers.bot.username:
                return True

        return False

    def handle(self, message: telegram.Message):
        message.reply_text('Чё?')
