from typing import Union

import telegram

from src import db
from src.handlers.database import handle_message
from src.helpers.message import Message

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


def reply_text(to: telegram.Message, msg: Union[str, Message]) -> telegram.Message:
    return send_message(to.chat_id, msg, to.message_id)


def send_message(chat_id: int, msg: Union[str, Message], reply_to: int = None) -> telegram.Message:
    if isinstance(msg, str):
        message = bot.send_message(chat_id, msg, reply_to_message_id=reply_to)
    else:
        message = msg.send(bot, chat_id, reply_to)

    handle_message(message)
    return message


def send_to_admins(text: str):
    with db.conn, db.conn.cursor() as cur:
        cur.execute('SELECT tg_id FROM users WHERE admin')
        for record in cur:
            send_message(record[0], text)


def is_reply_or_mention(message: telegram.Message) -> bool:
    if message.reply_to_message is not None and message.reply_to_message.from_user.id == bot.id:
        return True

    for entity in message.entities:
        if entity.type == 'mention' and message.text[entity.offset:entity.offset + entity.length] == '@' + bot.username:
            return True

    return False
