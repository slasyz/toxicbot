import re
from dataclasses import dataclass

import telegram
from loguru import logger

from toxic.handlers.database import DatabaseUpdateSaver
from toxic.handlers.handler import MessageHandler, CallbackHandler, CommandHandler
from toxic.helpers.rate_limiter import RateLimiter

from toxic.messenger.message import Message, TextMessage
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
                 update_handlers: list[DatabaseUpdateSaver],  # TODO: replace with interface
                 callbacks: list[CallbackDefinition],
                 commands: list[CommandDefinition],
                 useful_message_handlers: list[MessageHandler],
                 flood_message_handlers: list[MessageHandler],

                 users_repo: UsersRepository,
                 callback_data_repo: CallbackDataRepository,
                 messenger: Messenger,
                 metrics: Metrics,
                 rate_limiter: RateLimiter):
        self.update_handlers = update_handlers
        self.callbacks = callbacks
        self.commands = commands
        self.useful_message_handlers = useful_message_handlers
        self.flood_message_handlers = flood_message_handlers

        self.users_repo = users_repo
        self.callback_data_repo = callback_data_repo
        self.messenger = messenger
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

    def handle_command(self, text: str, message: telegram.Message) -> list[Message]:
        command_name = self._get_command_name(text, message)
        if command_name == '':
            return []

        args = ARGS_SPLIT_REGEXP.split(text[1:])

        for command in self.commands:
            if command_name != command.name:
                continue

            if message.from_user is None:
                break
            if command.handler.is_admins_only() and not self.users_repo.is_admin(message.from_user.id):
                break

            replies = self.rate_limiter.handle(message)
            if replies:
                return self._convert_handler_response(replies)

            return self._convert_handler_response(command.handler.handle(text, message, args))

        return []

    def handle_callback(self, callback: telegram.CallbackQuery):
        message = callback.message
        if message is None:
            return

        log_extra = {
            'user_id': callback.from_user.id,
            'chat_id': message.chat_id,
            'message_id': message.message_id,
        }

        if callback.data is None:
            return
        args_id = callback.data

        args = self.callback_data_repo.get_value(args_id)
        if args is None:
            return

        try:
            name = args['name']
        except KeyError as ex:
            logger.opt(exception=ex).error('Callback data does not contain "name" key.', **log_extra)
            return

        for callback_definition in self.callbacks:
            if callback_definition.name != name:
                continue

            if callback_definition.handler.is_admins_only() and not self.users_repo.is_admin(callback.from_user.id):
                callback.answer('Где ваши документы?', True)
                logger.error('Regular user sent admin-only callback.', user=callback.from_user.id, username=callback.from_user.username, callback=callback.id, data=callback.data)
                continue

            try:
                reply = callback_definition.handler.handle(callback, message, args)
                if reply is None:
                    return
                if isinstance(reply, Message):
                    self.messenger.send(message.chat_id, reply)
                    return
                callback.answer(text=reply.text, show_alert=reply.show_alert)
            except Exception as ex:
                logger.opt(exception=ex).error('Caught exception when handling callback.', **log_extra)
            return

    @staticmethod
    def _convert_handler_response(replies: list[Message] | str | None) -> list[Message]:
        if replies is None:
            return []
        if isinstance(replies, str):
            return [TextMessage(replies)]
        return replies

    def _handle_update_inner(self, update: telegram.Update):
        # Update handlers (like database)
        for updater in self.update_handlers:
            updater.handle(update)

        # Callback handlers
        if update.callback_query is not None:
            self.handle_callback(update.callback_query)
            return

        # Дальше обрабатываем только сообщения
        if update.message is None:
            return

        replies = []

        # Command handlers
        text = update.message.text
        if text is not None:
            try:
                replies += self.handle_command(text, update.message)
            except Exception as ex:
                replies.append(TextMessage('Ошибка.'))
                logger.opt(exception=ex).error('Caught exception when handling command.')

        # Useful message handlers (chain teaching, music links parser)
        for handler in self.useful_message_handlers:
            try:
                replies += self._convert_handler_response(handler.handle(text or '', update.message))
            except Exception as ex:
                replies.append(TextMessage('Ошибка.'))
                logger.opt(exception=ex).error('Caught exception when handling message by useful handler.')

        # Flood message handlers
        for handler in self.flood_message_handlers:
            if len(replies) > 0:
                break

            try:
                replies += self._convert_handler_response(handler.handle(text or '', update.message))
            except Exception as ex:
                replies.append(TextMessage('Ошибка.'))
                logger.opt(exception=ex).error('Caught exception when handling message by flood handler.')

        for reply in replies:
            try:
                self.messenger.send(update.message.chat_id, reply, update.message.message_id)
            except Exception as ex:
                logger.opt(exception=ex).error(
                    'Caught exception when replying to message.',
                    chat_id=update.message.chat_id,
                    message_id=update.message.message_id,
                )

    def handle_update(self, update: telegram.Update):
        with self.metrics.update_time.time():  # TODO: do with decorator
            self._handle_update_inner(update)
