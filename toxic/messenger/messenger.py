import time
from typing import Union

import telegram
from telegram.constants import MESSAGEENTITY_MENTION

from toxic.db import Database
from toxic.handlers.database import DatabaseUpdateSaver
from toxic.helpers.delayer import DelayerFactory
from toxic.messenger.message import TextMessage, Message, VoiceMessage

SYMBOLS_PER_SECOND = 20
MAX_DELAY = 4
DELAY_KEEPALIVE = 5


class Messenger:
    def __init__(self, bot: telegram.Bot, database: Database, dus: DatabaseUpdateSaver, delayer_factory: DelayerFactory):
        self.bot = bot
        self.database = database
        self.dus = dus
        self.delayer_factory = delayer_factory

    def reply(self, to: telegram.Message, msg: Union[str, Message], with_delay: bool = True) -> telegram.Message:
        return self.send(to.chat_id, msg, reply_to=to.message_id, with_delay=with_delay)

    def send(self, chat_id: int, msg: Union[str, Message], reply_to: int = None, with_delay: bool = True) -> telegram.Message:
        if isinstance(msg, str):
            msg = TextMessage(msg)

        if with_delay:
            length = msg.get_length()
            total_delay = min(length // SYMBOLS_PER_SECOND, MAX_DELAY)

            delayer = self.delayer_factory.create(total_delay, DELAY_KEEPALIVE)
            for interval in delayer:
                self.bot.send_chat_action(chat_id, msg.get_chat_action())
                # TODO: do it asynchronously
                time.sleep(interval)

        message = msg.send(self.bot, chat_id, reply_to)

        self.dus.handle_message(message)
        return message

    def send_to_admins(self, msg: Union[str, Message]):
        for row in self.database.query('SELECT tg_id FROM users WHERE admin'):
            self.send(row[0], msg)

    def is_reply_or_mention(self, message: telegram.Message) -> bool:
        if message.reply_to_message is not None and message.reply_to_message.from_user.id == self.bot.id:
            return True

        for entity in message.entities:
            if entity.type == MESSAGEENTITY_MENTION and message.text[entity.offset:entity.offset + entity.length] == '@' + self.bot.username:
                return True

        return False


def __main__():
    import main  # pylint: disable=import-outside-toplevel

    deps = main.init(['../../config.json'])

    deps.messenger.send(-328967401, 'приветики')


if __name__ == '__main__':
    __main__()
