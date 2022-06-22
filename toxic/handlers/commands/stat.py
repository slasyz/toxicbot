from __future__ import annotations

import re

import aiogram
from loguru import logger

from toxic.handlers.handler import CommandHandler, MessageHandler
from toxic.helpers import decorators
from toxic.messenger.message import Message
from toxic.repositories.chats import ChatsRepository
from toxic.repositories.users import UsersRepository


async def get_stat(chat_id: int, chats_repo: ChatsRepository) -> str:
    response = ''
    async for name, count in chats_repo.get_stat(chat_id):
        response += f'\n{name} — {count} сообщ.'

    return response


class StatCommand(CommandHandler):
    def __init__(self, users_repo: UsersRepository, chats_repo: ChatsRepository):
        self.users_repo = users_repo
        self.chats_repo = chats_repo

    async def _get_response(self, chat_id) -> str:
        response = 'Статистика чата:\n'
        response += await get_stat(chat_id, self.chats_repo)
        return response

    async def _parse_args_and_send(self, args: list[str]) -> str:
        try:
            chat_id = int(args[1])
        except ValueError:
            return f'Нужно писать так: /{args[0]} CHAT_ID'

        return await self._get_response(chat_id)

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        if message.chat.id < 0:
            if len(args) == 1:
                return await self._get_response(message.chat.id)
            if len(args) == 2:
                return await self._parse_args_and_send(args)
            return None

        if message.from_user is None:
            logger.error('Empty from_user in /stat command.', message_id=message.message_id, chat_id=message.chat.id)
            return 'Что-то не то.'

        if not await self.users_repo.is_admin(message.from_user.id):
            return 'Это нужно делать в общем чате.'

        if len(args) != 2:
            return f'Нужно писать так: /{args[0]} [CHAT_ID]'

        return await self._parse_args_and_send(args)


# TODO: unify with StatsCommand, maybe rename handle to handle_command+handle_message
class StatsHandler(MessageHandler):
    def __init__(self, replies: dict[re.Pattern, str], chats_repo: ChatsRepository):
        self.replies = replies
        self.chats_repo = chats_repo

    @staticmethod
    def new(replies: dict[str, str], chats_repo: ChatsRepository) -> StatsHandler:
        replies_regexes: dict[re.Pattern, str] = {}

        for key, value in replies.items():
            regexp = re.compile(key)
            replies_regexes[regexp] = value

        return StatsHandler(replies_regexes, chats_repo)

    @decorators.non_empty
    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        # pylint: disable=W0221
        # Because of the decorator
        for key, value in self.replies.items():
            if key.search(text.lower()) is None:
                continue

            response = value + ':\n'
            response += await get_stat(message.chat.id, self.chats_repo)

            return response

        return None
