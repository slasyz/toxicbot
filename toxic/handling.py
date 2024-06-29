import re
from dataclasses import dataclass

import aiogram
from loguru import logger

from toxic.db import Database
from toxic.helpers import consts_tg
from toxic.helpers.rate_limiter import RateLimiter
from toxic.interfaces import CommandHandler, CallbackHandler, MessageHandler
from toxic.messenger.message import Message, TextMessage
from toxic.messenger.messenger import Messenger
from toxic.metrics import Metrics
from toxic.modules.dus.dus import DatabaseUpdateSaver
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


@dataclass
class Reply:
    source: str
    message: Message


class HandlersManager:
    def __init__(self,
                 update_handlers: list[DatabaseUpdateSaver],  # TODO: replace with interface
                 callbacks: list[CallbackDefinition],
                 commands: list[CommandDefinition],
                 useful_message_handlers: list[MessageHandler],
                 flood_message_handlers: list[MessageHandler],

                 users_repo: UsersRepository,
                 database: Database,
                 messenger: Messenger,
                 metrics: Metrics,
                 rate_limiter: RateLimiter):
        self.update_handlers = update_handlers
        self.callbacks = callbacks
        self.commands = commands
        self.useful_message_handlers = useful_message_handlers
        self.flood_message_handlers = flood_message_handlers

        self.users_repo = users_repo
        self.database = database
        self.messenger = messenger
        self.metrics = metrics
        self.rate_limiter = rate_limiter

    async def _get_command_name(self, text: str, message: aiogram.types.Message) -> str:
        # Проходимся по всем сущностям, если на первом месте в сообщении есть сущность типа 'bot_command', то записываем
        # название команды.
        if message.entities is None:
            return ''
        for entity in message.entities:
            if entity.offset != 0:
                continue

            if entity.type != consts_tg.MESSAGEENTITY_BOT_COMMAND:
                continue

            command_name = text[1:entity.length]  # trim leading slash
            if '@' in command_name:
                command_name, command_target = command_name.split('@', 2)
                if command_target != (await self.messenger.bot.me()).username:
                    continue

            return command_name
        return ''

    async def handle_command(self, text: str, message: aiogram.types.Message) -> list[Message]:
        command_name = await self._get_command_name(text, message)
        if command_name == '':
            return []

        args = ARGS_SPLIT_REGEXP.split(text[1:])

        for command in self.commands:
            if command_name != command.name:
                continue

            if message.from_user is None:
                break
            if command.handler.is_admins_only() and not await self.users_repo.is_admin(message.from_user.id):
                break

            replies = self.rate_limiter.handle(message)
            if replies:
                return self._convert_handler_response(replies)

            return self._convert_handler_response(await command.handler.handle(text, message, args))

        return []

    async def _get_callback_value(self, uuid: str) -> dict | None:
        row = await self.database.query_row('SELECT value FROM callback_data WHERE uuid=$1', (uuid,))
        if row is None:
            return None

        return row[0]

    async def handle_callback(self, callback: aiogram.types.CallbackQuery):
        message = callback.message
        if message is None:
            return

        log_extra = {
            'user_id': callback.from_user.id,
            'chat_id': message.chat.id,
            'message_id': message.message_id,
        }

        if callback.data is None:
            return
        args_id = callback.data

        args = await self._get_callback_value(args_id)
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

            if callback_definition.handler.is_admins_only() and not await self.users_repo.is_admin(callback.from_user.id):
                await self.messenger.answer_callback(callback.id, 'Где ваши документы?', True)
                logger.error('Regular user sent admin-only callback.',
                             user=callback.from_user.id,
                             username=callback.from_user.username,
                             callback=callback.id,
                             data=callback.data)
                continue

            try:
                reply = await callback_definition.handler.handle(callback, message, args)
                if reply is None:
                    return
                if isinstance(reply, Message):
                    await self.messenger.send(message.chat.id, reply)
                    return
                await self.messenger.answer_callback(callback.id, text=reply.text, show_alert=reply.show_alert)
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

    async def _handle_update_inner(self, update: aiogram.types.Update):
        # Update handlers (like database)
        for updater in self.update_handlers:
            try:
                await updater.handle(update)
            except Exception as ex:
                logger.opt(exception=ex).error('Caught exception when handling update by update handler.')

        # Callback handlers
        if update.callback_query is not None:
            await self.handle_callback(update.callback_query)
            return

        # Дальше обрабатываем только сообщения
        if update.message is None:
            return

        replies = []

        # Command handlers
        text = update.message.text
        if text is not None:
            try:
                replies += [Reply('command', x) for x in await self.handle_command(text, update.message)]
            except Exception as ex:
                replies.append(Reply('command', TextMessage('Ошибка.')))
                logger.opt(exception=ex).error('Caught exception when handling command.')

        # Useful message handlers (chain teaching, music links parser)
        for handler in self.useful_message_handlers:
            try:
                replies += [Reply(handler.__class__.__name__, x) for x in self._convert_handler_response(await handler.handle(text or '', update.message))]
            except Exception as ex:
                replies.append(Reply(handler.__class__.__name__, TextMessage('Ошибка.')))
                logger.opt(exception=ex).error('Caught exception when handling message by useful handler.')

        # Flood message handlers
        for handler in self.flood_message_handlers:
            if len(replies) > 0:
                break

            try:
                replies += [Reply(handler.__class__.__name__, x) for x in self._convert_handler_response(await handler.handle(text or '', update.message))]
            except Exception as ex:
                replies.append(Reply(handler.__class__.__name__, TextMessage('Ошибка.')))
                logger.opt(exception=ex).error('Caught exception when handling message by flood handler.')

        for reply in replies:
            logger.info(f'Replying {reply.source} -> {update.message.chat.id}:{update.message.message_id}.')
            try:
                await self.messenger.send(update.message.chat.id, reply.message, update.message.message_id)
            except Exception as ex:
                logger.opt(exception=ex).error(
                    'Caught exception when replying to message.',
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id,
                )

    async def handle_update(self, update: aiogram.types.Update):
        with self.metrics.update_time.time():  # TODO: do with decorator
            await self._handle_update_inner(update)
