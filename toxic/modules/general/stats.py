from __future__ import annotations

import re

import aiogram
from loguru import logger

from toxic.db import Database
from toxic.interfaces import CommandHandler, MessageHandler
from toxic.messenger.message import Message
from toxic.repository import Repository


async def get_stat(chat_id: int, database: Database) -> str:
    response = ''
    rows = await database.query('''
        SELECT btrim(concat(u.first_name, ' ', u.last_name)), count(m.*) as c
        FROM messages m
            JOIN users u ON m.user_id = u.tg_id
        WHERE m.chat_id=$1
        GROUP BY user_id, u.first_name, u.last_name
        ORDER BY c DESC
        LIMIT 10;
    ''', (chat_id,))
    for name, count in rows:
        response += f'\n{name} — {count} сообщ.'

    return response


class StatCommand(CommandHandler):
    def __init__(self, repo: Repository, database: Database):
        self.repo = repo
        self.database = database

    async def _get_response(self, chat_id) -> str:
        response = 'Статистика чата:\n'
        response += await get_stat(chat_id, self.database)
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

        if not await self.repo.is_admin(message.from_user.id):
            return 'Это нужно делать в общем чате.'

        if len(args) != 2:
            return f'Нужно писать так: /{args[0]} [CHAT_ID]'

        return await self._parse_args_and_send(args)


# TODO: unify with StatsCommand, maybe rename handle to handle_command+handle_message
class StatsHandler(MessageHandler):
    def __init__(self, replies: dict[re.Pattern, str], database: Database):
        self.replies = replies
        self.database = database

    @staticmethod
    def new(replies: dict[str, str], database: Database) -> StatsHandler:
        replies_regexes: dict[re.Pattern, str] = {}

        for key, value in replies.items():
            regexp = re.compile(key)
            replies_regexes[regexp] = value

        return StatsHandler(replies_regexes, database)

    async def handle(self, text: str, message: aiogram.types.Message) -> str | list[Message] | None:
        if text == '':
            return None

        for key, value in self.replies.items():
            if key.search(text.lower()) is None:
                continue

            response = value + ':\n'
            response += await get_stat(message.chat.id, self.database)

            return response

        return None
