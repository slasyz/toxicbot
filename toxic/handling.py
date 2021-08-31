import logging
import re
from dataclasses import dataclass
from typing import Tuple

import telegram

from toxic.db import Database
from toxic.handlers.commands.command import Command
from toxic.handlers.database import DatabaseUpdateSaver
from toxic.handlers.handler import Handler
from toxic.helpers.rate_limiter import RateLimiter
from toxic.messenger import Messenger
from toxic.metrics import Metrics

ARGS_SPLIT_REGEXP = re.compile(r'\s+')


@dataclass
class CommandDefinition:
    name: str
    handler: Command
    admins_only: bool


class HandlersManager:
    def __init__(self,
                 handlers_private: Tuple[Handler, ...],
                 handlers_chats: Tuple[Handler, ...],
                 commands: Tuple[CommandDefinition, ...],
                 database: Database,
                 messenger: Messenger,
                 dus: DatabaseUpdateSaver,
                 metrics: Metrics,
                 rate_limiter: RateLimiter):
        self.handlers_private = handlers_private
        self.handlers_chats = handlers_chats
        self.commands = commands
        self.database = database
        self.messenger = messenger
        self.dus = dus
        self.metrics = metrics
        self.rate_limiter = rate_limiter

    def handle_command(self, message: telegram.Message) -> bool:
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
                if command_target != self.messenger.bot.username:
                    continue

            break

        if command_name == '':
            return False

        args = ARGS_SPLIT_REGEXP.split(message.text[1:])

        for command in self.commands:
            if command_name != command.name:
                continue

            if command.admins_only and not self.database.is_admin(message.from_user.id):
                break

            if self.rate_limiter.handle(message):
                return True

            command.handler.handle(message, args)
            return True

        return False

    def _handle_update_inner(self, update: telegram.Update):
        self.metrics.updates.inc(1)
        # Пишем в БД
        self.dus.handle(update)

        # Обрабатываем только сообщения
        if update.message is None:
            return

        # Обрабатываем команду
        if update.message.text is not None:
            if self.handle_command(update.message):
                return

        # Обрабатываем сообщение

        if update.message.chat_id > 0:
            handlers = self.handlers_private
        else:
            handlers = self.handlers_chats

        for handler in handlers:
            try:
                handler.pre_handle(update.message)

                if handler.handle(update.message):
                    return
            except Exception as ex:
                self.messenger.reply(update.message, 'Ошибка.')
                logging.error('Caught exception when handling update.', exc_info=ex)

    def handle_update(self, update: telegram.Update):
        with self.metrics.update_time.time():  # TODO: do with decorator
            self._handle_update_inner(update)