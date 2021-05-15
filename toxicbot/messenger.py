import logging
import time
import traceback
from typing import Union

import telegram
from telegram.constants import CHATACTION_TYPING, CHATACTION_RECORD_VOICE

from toxicbot.db import Database
from toxicbot.features.voice import NextUpService
from toxicbot.handlers.database import DatabaseUpdateSaver

DEFAULT_DELAY = 2
SYMBOLS_PER_SECOND = 7


class Message:
    def get_chat_action(self) -> str:
        raise NotImplementedError()

    def get_length(self) -> int:
        raise NotImplementedError()

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        raise NotImplementedError()


class VoiceMessage(Message):
    def __init__(self, text, service=None):
        self.text = text
        self.service = service or NextUpService()

    def get_chat_action(self) -> str:
        return CHATACTION_RECORD_VOICE

    def get_length(self) -> int:
        return len(self.text)

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

    def get_length(self) -> int:
        return len(self.text)

    def get_chat_action(self) -> str:
        return CHATACTION_TYPING

    def send(self, bot: telegram.Bot, chat_id: int, reply_to: int = None) -> telegram.Message:
        return bot.send_message(chat_id, self.text, reply_to_message_id=reply_to)


class Messenger:
    def __init__(self, bot: telegram.Bot, database: Database, dum: DatabaseUpdateSaver):
        self.bot = bot
        self.database = database
        self.dum = dum

    def reply(self, to: telegram.Message, msg: Union[str, Message], delay: bool) -> telegram.Message:
        return self.send(to.chat_id, msg, reply_to=to.message_id, with_delay=delay)

    def send(self, chat_id: int, msg: Union[str, Message], reply_to: int = None, with_delay: bool = False) -> telegram.Message:
        if isinstance(msg, str):
            msg = TextMessage(msg)

        if with_delay:
            length = msg.get_length()
            delay = length / SYMBOLS_PER_SECOND

            self.bot.send_chat_action(chat_id, msg.get_chat_action())
            # TODO: do it asynchronously
            time.sleep(delay)

        message = msg.send(self.bot, chat_id, reply_to)

        self.dum.handle_message(message)
        return message

    def send_to_admins(self, msg: Union[str, Message]):
        for row in self.database.query('SELECT tg_id FROM users WHERE admin'):
            self.send(row[0], msg)

    def is_reply_or_mention(self, message: telegram.Message) -> bool:
        if message.reply_to_message is not None and message.reply_to_message.from_user.id == self.bot.id:
            return True

        for entity in message.entities:
            if entity.type == 'mention' and message.text[entity.offset:entity.offset + entity.length] == '@' + self.bot.username:
                return True

        return False


def __main__():
    import main  # pylint: disable=import-outside-toplevel

    _, _, messenger, _, _ = main.init(['../../config.json'])

    messenger.send(-362750796, VoiceMessage('приветики'))


if __name__ == '__main__':
    __main__()
