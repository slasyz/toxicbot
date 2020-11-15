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


def __main__():
    import os  # pylint: disable=import-outside-toplevel
    import time  # pylint: disable=import-outside-toplevel

    import telegram  # pylint: disable=import-outside-toplevel

    from src import db  # pylint: disable=import-outside-toplevel
    from src.helpers import general  # pylint: disable=import-outside-toplevel
    from src import config  # pylint: disable=import-outside-toplevel
    from src.helpers import log  # pylint: disable=import-outside-toplevel

    log.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()

    config.load('../../config.json')
    db.connect()

    general.bot = telegram.Bot(config.c['telegram']['token'])

    general.send(-328967401, VoiceMessage('приветик, чикуля-красотка, чем занимаешься?'))


if __name__ == '__main__':
    __main__()
