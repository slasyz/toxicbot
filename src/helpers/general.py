import re
from typing import Union

import telegram

from src import db
from src.handlers.database import handle_message
from src.helpers.message import Message

LINK_REGEXP = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')

bot: Union[telegram.Bot, type(None)] = None


def non_empty(func):
    """
    Checks if message contains text before calling wrapping function.  If it does not contain it, returns False.
    """

    def wrapper(self, message: telegram.Message):
        if message.text is None:
            return False

        return func(self, message)

    return wrapper


def is_admin(user_id: int) -> bool:
    with db.conn, db.conn.cursor() as cur:
        cur.execute('SELECT true FROM users WHERE tg_id=%s AND admin', (user_id,))
        return cur.fetchone() is not None


def reply(to: telegram.Message, msg: Union[str, Message]) -> telegram.Message:
    return send(to.chat_id, msg, to.message_id)


def send(chat_id: int, msg: Union[str, Message], reply_to: int = None) -> telegram.Message:
    if isinstance(msg, str):
        message = bot.send_message(chat_id, msg, reply_to_message_id=reply_to)
    else:
        message = msg.send(bot, chat_id, reply_to)

    handle_message(message)
    return message


def send_to_admins(msg: Union[str, Message]):
    with db.conn, db.conn.cursor() as cur:
        cur.execute('SELECT tg_id FROM users WHERE admin')
        for record in cur:
            send(record[0], msg)


def is_reply_or_mention(message: telegram.Message) -> bool:
    if message.reply_to_message is not None and message.reply_to_message.from_user.id == bot.id:
        return True

    for entity in message.entities:
        if entity.type == 'mention' and message.text[entity.offset:entity.offset + entity.length] == '@' + bot.username:
            return True

    return False
