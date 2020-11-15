import logging
import traceback

import telegram

from src.features.voice import NextUpService


class Message:
    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        raise NotImplementedError()


class VoiceMessage(Message):
    def __init__(self, text, service=None):
        self.text = text
        self.service = service or NextUpService()

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        try:
            f = self.service.load(self.text)
            return bot.send_voice(chat_id, voice=f, reply_to_message_id=reply_to)
        except Exception as e:
            logging.error('caught exception %s:\n\n%s', e, traceback.format_exc())
            return bot.send_message(chat_id, f'(Хотел записать голосовуху, не получилось)\n\n{self.text}')
