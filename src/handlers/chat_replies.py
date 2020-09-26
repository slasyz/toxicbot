import random
import re

import telegram

from src.helpers import general

NAHUY_REGEXP = r'(иди|пошел|пошла|пошёл)\s+(на\s?хуй|в\s?пизду|в\s?ж[еоё]пп?у)'
NAHUY_ANSWER = 'Что за токсичность...'


class NahuyHandler:
    @general.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if re.search(NAHUY_REGEXP, message.text.lower()) is None:
            return False

        general.reply_text(message, NAHUY_ANSWER)
        return True


class PidorHandler:
    @general.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if 'пидор' not in message.text.lower():
            return False

        general.reply_text(message, 'Пошёл нахуй.')
        return True


PRIVATE_ANSWERS = [
    'Сделаю вид, что я этого не заметил.',
    'Давай притворимся, будто этого не было.',
    'Щас пожалуюсь Славе, что ты до меня домогаешься.'
]


class PrivateHandler:
    def handle(self, message: telegram.Message):
        if general.is_admin(message.chat_id):
            general.reply_text(message, 'Я запущен')
        else:
            general.reply_text(message, random.choice(PRIVATE_ANSWERS))
        return True


VOICE_ANSWERS = [
    'И что, мы должны щас все бросить свои дела и слушать это?',
    'Зумеры совсем обезумели, буквы печатать разучились.',
    'Напиши текстом.',
    'Бляяя...',
]


class VoiceHandler:
    def handle(self, message: telegram.Message) -> bool:
        if message.voice is None and message.video_note is None:
            return False

        general.reply_text(message, random.choice(VOICE_ANSWERS))
        return True


SORRY_REGEXP = r'бот,\s+извинись'


class SorryHandler:
    @general.non_empty
    def handle(self, message: telegram.Message) -> bool:
        if message.chat_id > 0:
            general.send_message(message.chat_id, 'Отсоси, потом проси.')
            return True

        if re.search(SORRY_REGEXP, message.text.lower()) is not None:
            general.send_message(message.chat_id, 'Извините.')
            return True

        if general.is_reply_or_mention(message) and 'извинись' in message.text.lower():
            general.send_message(message.chat_id, 'Извините.')
            return True

        return False
