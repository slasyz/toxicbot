import re
from dataclasses import dataclass

import telegram
from loguru import logger

from toxic.handlers.database import DatabaseUpdateSaver
from toxic.handlers.handler import MessageHandler, CallbackHandler, CommandHandler
from toxic.helpers.rate_limiter import RateLimiter
from toxic.messenger.messenger import Messenger
from toxic.metrics import Metrics
from toxic.repositories.callback_data import CallbackDataRepository
from toxic.repositories.users import UsersRepository

ARGS_SPLIT_REGEXP = re.compile(r'\s+')


@dataclass
class CommandDefinition:
    name: str
    handler: CommandHandler


@dataclass
class CallbackDefinition:
    name: str
    handler: CallbackHandler


class HandlersManager:
    def __init__(self,
                 handlers_private: tuple[MessageHandler, ...],
                 handlers_chats: tuple[MessageHandler, ...],
                 commands: tuple[CommandDefinition, ...],
                 callbacks: tuple[CallbackDefinition, ...],
                 users_repo: UsersRepository,
                 callback_data_repo: CallbackDataRepository,
                 messenger: Messenger,
                 dus: DatabaseUpdateSaver,
                 metrics: Metrics,
                 rate_limiter: RateLimiter):
        self.handlers_private = handlers_private
        self.handlers_chats = handlers_chats
        self.commands = commands
        self.callbacks = callbacks
        self.users_repo = users_repo
        self.callback_data_repo = callback_data_repo
        self.messenger = messenger
        self.dus = dus
        self.metrics = metrics
        self.rate_limiter = rate_limiter

    def _get_command_name(self, text: str, message: telegram.Message) -> str:
        # Проходимся по всем сущностям, если на первом месте в сообщении есть сущность типа 'bot_command', то записываем
        # название команды.
        for entity in message.entities:
            if entity.offset != 0:
                continue

            if entity.type != telegram.MessageEntity.BOT_COMMAND:
                continue

            command_name = text[1:entity.length]  # trim leading slash
            if '@' in command_name:
                command_name, command_target = command_name.split('@', 2)
                if command_target != self.messenger.bot.username:
                    continue

            return command_name
        return ''

    def handle_command(self, text: str, message: telegram.Message) -> bool:
        command_name = self._get_command_name(text, message)
        if command_name == '':
            return False

        args = ARGS_SPLIT_REGEXP.split(text[1:])

        for command in self.commands:
            if command_name != command.name:
                continue

            if message.from_user is None:
                break
            if command.handler.is_admins_only() and not self.users_repo.is_admin(message.from_user.id):
                break

            if self.rate_limiter.handle(message):
                return True

            try:
                command.handler.handle(text, message, args)
            except Exception as ex:
                logger.opt(exception=ex).error('Caught exception when handling command.')
            return True

        return False

    def handle_callback(self, callback: telegram.CallbackQuery):
        message = callback.message
        if message is None:
            return False

        log_extra = {
            'user_id': callback.from_user.id,
            'chat_id': message.chat_id,
            'message_id': message.message_id,
        }

        if callback.data is None:
            return False
        args_id = int(callback.data)

        args = self.callback_data_repo.get_value(args_id)
        if args is None:
            return False

        try:
            name = args['name']
        except KeyError as ex:
            logger.opt(exception=ex).error('Callback data does not contain "name" key.', **log_extra)
            return False

        for callback_definition in self.callbacks:
            if callback_definition.name != name:
                continue

            if callback_definition.handler.is_admins_only() and not self.users_repo.is_admin(callback.from_user.id):
                # TODO: log
                continue

            try:
                callback_definition.handler.handle(callback, message, args)
            except Exception as ex:
                logger.opt(exception=ex).error('Caught exception when handling callback.', **log_extra)
            return True

    def _handle_update_inner(self, update: telegram.Update):
        self.metrics.updates.inc(1)
        # Пишем в БД
        self.dus.handle(update)

        # Обрабатываем коллбэк
        if update.callback_query is not None:
            if self.handle_callback(update.callback_query):
                return

        # Обрабатываем только сообщения
        if update.message is None:
            return

        # Обрабатываем команду
        text = update.message.text
        if text is not None:
            if self.handle_command(text, update.message):
                return

        # Обрабатываем сообщение

        if update.message.chat_id > 0:
            handlers = self.handlers_private
        else:
            handlers = self.handlers_chats

        for handler in handlers:
            try:
                handler.pre_handle(update.message)
            except Exception as ex:
                self.messenger.reply(update.message, 'Ошибка.')
                logger.opt(exception=ex).error('Caught exception when handling update.')

        for handler in handlers:
            try:
                if handler.handle(update.message):
                    return
            except Exception as ex:
                self.messenger.reply(update.message, 'Ошибка.')
                logger.opt(exception=ex).error('Caught exception when handling update.')

    def handle_update(self, update: telegram.Update):
        with self.metrics.update_time.time():  # TODO: do with decorator
            self._handle_update_inner(update)
