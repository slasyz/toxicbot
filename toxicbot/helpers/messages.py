import logging
import time
import traceback
from typing import Union

import telegram

from toxicbot import db
from toxicbot.features.voice import NextUpService
from toxicbot.helpers import general
from toxicbot.handlers.database import handle_message


DEFAULT_DELAY = 2


class Message:
    def get_chat_action(self) -> str:
        raise NotImplementedError()

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        raise NotImplementedError()


class VoiceMessage(Message):
    def __init__(self, text, service=None):
        self.text = text
        self.service = service or NextUpService()

    def get_chat_action(self) -> str:
        return 'record_voice'

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        try:
            f = self.service.load(self.text)
            return bot.send_voice(chat_id, voice=f, reply_to_message_id=reply_to)
        except Exception as ex:
            logging.error('caught exception %s:\n\n%s', ex, traceback.format_exc())
            return bot.send_message(chat_id, f'(Хотел записать голосовуху, не получилось)\n\n{self.text}')


class TextMessage(Message):
    def __init__(self, text):
        self.text = text

    def get_chat_action(self) -> str:
        return 'typing'

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        return general.bot.send_message(chat_id, self.text, reply_to_message_id=reply_to)


def reply(to: telegram.Message, msg: Union[str, Message], delay: int = DEFAULT_DELAY) -> telegram.Message:
    return send(to.chat_id, msg, reply_to=to.message_id, delay=delay)


def send(chat_id: int, msg: Union[str, Message], reply_to: int = None, delay: int = DEFAULT_DELAY) -> telegram.Message:
    if isinstance(msg, str):
        msg = TextMessage(msg)

    if delay > 0:
        general.bot.send_chat_action(chat_id, msg.get_chat_action())
        # TODO: do it asynchronously
        time.sleep(delay)

    message = msg.send(general.bot, chat_id, reply_to)

    handle_message(message)
    return message


def send_to_admins(msg: Union[str, Message]):
    with db.conn, db.conn.cursor() as cur:
        cur.execute('SELECT tg_id FROM users WHERE admin')
        for record in cur:
            send(record[0], msg)


def is_reply_or_mention(message: telegram.Message) -> bool:
    if message.reply_to_message is not None and message.reply_to_message.from_user.id == general.bot.id:
        return True

    for entity in message.entities:
        if entity.type == 'mention' and message.text[entity.offset:entity.offset + entity.length] == '@' + general.bot.username:
            return True

    return False


def __main__():
    from toxicbot import config  # pylint: disable=import-outside-toplevel
    import main  # pylint: disable=import-outside-toplevel

    main.init('../../config.json')

    general.bot = telegram.Bot(config.c['telegram']['token'])

    send(-362750796, VoiceMessage('приветики'))


if __name__ == '__main__':
    __main__()
