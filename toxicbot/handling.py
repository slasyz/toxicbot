import logging
import traceback
import re
from dataclasses import dataclass
from typing import Tuple

import telegram

from toxicbot.handlers.chain import ChainHandler
from toxicbot.handlers.commands.command import Command
from toxicbot.handlers.handler import Handler
from toxicbot.helpers import general
from toxicbot.helpers.general import is_admin
from toxicbot.helpers.messages import reply
from toxicbot.handlers import database
from toxicbot.handlers.commands.joke import JokeCommand
from toxicbot.handlers.commands.chats import ChatsCommand
from toxicbot.handlers.commands.dump import DumpCommand
from toxicbot.handlers.commands.send import SendCommand
from toxicbot.handlers.commands.stat import StatCommand, PizditHandler
from toxicbot.handlers.chat_replies import NahuyHandler, PidorHandler, PrivateHandler, VoiceHandler, SorryHandler
from toxicbot.features.chain.splitters import PunctuationSplitter


ARGS_SPLIT_REGEXP = re.compile(r'\s+')


@dataclass
class CommandDefinition:
    name: str
    handler: Command
    admins_only: bool


handlers_private: Tuple[Handler, ...] = ()
handlers_chats: Tuple[Handler, ...] = ()
commands: Tuple[CommandDefinition, ...] = ()


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

    args = ARGS_SPLIT_REGEXP.split(message.text[1:])

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
            handler.pre_handle(update.message)

            if handler.handle(update.message):
                return
        except Exception as ex:
            reply(update.message, 'Ошибка.')
            logging.error('caught exception %s:\n\n%s', ex, traceback.format_exc())


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
        ChainHandler(window=3, splitter=PunctuationSplitter()),
    )

    commands = (
        CommandDefinition('dump', DumpCommand(), True),
        CommandDefinition('stat', StatCommand(), False),
        CommandDefinition('joke', JokeCommand(), False),
        CommandDefinition('send', SendCommand(), True),
        CommandDefinition('chats', ChatsCommand(), True),
    )
