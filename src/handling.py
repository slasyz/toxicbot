import logging
import traceback
import re
from collections import namedtuple

import telegram

from src.handlers.chain import ChainHandler
from src.helpers import general
from src.helpers.general import is_admin, reply_text
from src.handlers import database
from src.handlers.commands.anecdote import AnecdoteCommand
from src.handlers.commands.chats import ChatsCommand
from src.handlers.commands.dump import DumpCommand
from src.handlers.commands.send import SendCommand
from src.handlers.commands.stat import StatCommand, PizditHandler
from src.handlers.chat_replies import NahuyHandler, PidorHandler, PrivateHandler, VoiceHandler, SorryHandler
from src.services.chain.splitters import NoPunctuationSplitter


class Command(namedtuple('Command', ['name', 'handler', 'admins_only'])):
    pass


handlers_private = ()
handlers_chats = ()
commands = ()


def handle_command(message: telegram.Message) -> bool:
    command_name = ''

    # Проходимся по всем сущностям, если на первом месте в сообщении есть сущность типа 'bot_command', то записываем
    # название команды.
    for entity in message.entities:
        if entity['offset'] != 0:
            continue

        if entity['type'] != telegram.MessageEntity.BOT_COMMAND:
            continue

        command_name = message.text[1:entity['length']]
        if '@' in command_name:
            command_name, command_target = command_name.split('@', 2)
            if command_target != general.bot.username:
                continue

        break

    if command_name == '':
        return False

    args = re.split(r'\s+', message.text[1:])

    for command in commands:
        if command_name != command.name:
            continue

        if command.admins_only and not is_admin(message.from_user.id):
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
    if update.message.text is not None:
        if handle_command(update.message):
            return

    # Обрабатываем сообщение

    if update.message.chat_id > 0:
        handlers = handlers_private
    else:
        handlers = handlers_chats

    for handler in handlers:
        try:
            if 'pre_handle' in dir(handler):
                handler.pre_handle(update.message)

            if handler.handle(update.message):
                return
        except Exception as e:
            reply_text(update.message, 'Ошибка.')
            logging.error('caught exception %s:\n\n%s', e, traceback.format_exc())


def init():
    global handlers_private
    global handlers_chats
    global commands

    handlers_private = (
        PrivateHandler(),
    )

    handlers_chats = (
        VoiceHandler(),
        NahuyHandler(),
        PidorHandler(),
        SorryHandler(),
        PizditHandler(),
        ChainHandler(window=1, splitter=NoPunctuationSplitter()),
    )

    commands = (
        Command('dump', DumpCommand(), True),
        Command('stat', StatCommand(), False),
        Command('joke', AnecdoteCommand(), False),
        Command('send', SendCommand(), True),
        Command('chats', ChatsCommand(), True),
    )
