import random
import re

import telegram

from src import helpers

NAHUY_REGEXP = r'(иди|пошел|пошла|пошёл)\s+(на\s?хуй|в\s?пизду|в\s?ж[еоё]пп?у)'
NAHUY_ANSWER = 'Что за токсичность...'


class NahuyHandler:
    @helpers.non_empty
    def match(self, message: telegram.Message) -> bool:
        return re.search(NAHUY_REGEXP, message.text.lower()) is not None

    def handle(self, message: telegram.Message):
        helpers.reply_text(message, NAHUY_ANSWER)


class PidorHandler:
    @helpers.non_empty
    def match(self, message: telegram.Message) -> bool:
        return 'пидор' in message.text.lower()

    def handle(self, message: telegram.Message):
        helpers.reply_text(message, 'Пошёл нахуй.')


PRIVATE_ANSWERS = [
    'Сделаю вид, что я этого не заметил.',
    'Давай притворимся, будто этого не было.',
    'Щас пожалуюсь Славе, что ты до меня домогаешься.'
]


class PrivateHandler:
    def match(self, message: telegram.Message) -> bool:
        return True

    def handle(self, message: telegram.Message):
        if helpers.is_admin(message.chat_id):
            helpers.reply_text(message, 'Я запущен')
        else:
            helpers.reply_text(message, random.choice(PRIVATE_ANSWERS))


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
        helpers.reply_text(message, random.choice(VOICE_ANSWERS))


SORRY_REGEXP = r'бот,\s+извинись'


class SorryHandler:
    @helpers.non_empty
    def match(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            helpers.send_message(message.chat_id, 'Отсоси, потом проси.')
            return True

        if re.search(SORRY_REGEXP, message.text.lower()) is not None:
            helpers.send_message(message.chat_id, 'Извините.')
            return True

        if helpers.is_reply_or_mention(message) and 'извинись' in message.text.lower():
            helpers.send_message(message.chat_id, 'Извините.')
            return True

        return False

    def handle(self, message: telegram.Message):
        pass
