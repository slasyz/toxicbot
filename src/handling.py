import logging
import traceback
import re
from collections import namedtuple

import telegram

from src.helpers import is_admin
from src.handlers import database
from src.handlers.commands.anecdote import AnecdoteCommand
from src.handlers.commands.dump import DumpCommand
from src.handlers.commands.stat import StatCommand
from src.handlers.chat_replies import NahuyHandler, PidorHandler, PrivateHandler, VoiceHandler, MentionHandler


class Command(namedtuple('Command', ['name', 'handler', 'admins_only'])):
    pass


handlers_private = (
    PrivateHandler(),
)


handlers_chats = (
    VoiceHandler(),
    NahuyHandler(),
    PidorHandler(),
    MentionHandler(),
)


commands = (
    Command('dump', DumpCommand(), True),
    Command('stat', StatCommand(), False),
    Command('joke', AnecdoteCommand(), False),
)


def handle_command(message: telegram.Message) -> bool:
    args = re.split(r'\s+', message.text[1:])

    for command in commands:
        if args[0] != command.name:
            continue

        if command.admins_only and is_admin(message.from_user.id):
            break

        command.handler.handle(message, args)
        return True

    return False


def handle_update(update: telegram.Update):
    # Пишем в БД
    database.handle(update)

    # Обрабатываем только новые сообщения
    if update.message is None:
        return

    # Обрабатываем команду
    if update.message.text is not None and update.message.text.startswith('/'):
        if handle_command(update.message):
            return

    # Обрабатываем сообщение

    if update.message.chat_id > 0:
        handlers = handlers_private
    else:
        handlers = handlers_chats

    for handler in handlers:
        try:
            if handler.match(update.message):
                handler.handle(update.message)
                return
        except Exception as e:
            logging.error(str(e) + '\n\n' + traceback.format_exc())
