from __future__ import annotations

import re

import telegram
from loguru import logger

from toxic.handlers.handler import CommandHandler, MessageHandler
from toxic.helpers import decorators
from toxic.messenger.messenger import Messenger
from toxic.repositories.chats import ChatsRepository
from toxic.repositories.users import UsersRepository


def get_stat(chat_id: int, chats_repo: ChatsRepository) -> str:
    response = ''
    for name, count in chats_repo.get_stat(chat_id):
        response += f'\n{name} — {count} сообщ.'

    return response


class StatCommand(CommandHandler):
    def __init__(self, users_repo: UsersRepository, chats_repo: ChatsRepository, messenger: Messenger):
        self.users_repo = users_repo
        self.chats_repo = chats_repo
        self.messenger = messenger

    def _get_response(self, chat_id) -> str:
        response = 'Статистика чата:\n'
        response += get_stat(chat_id, self.chats_repo)
        return response

    def _parse_args_and_send(self, message: telegram.Message, args: list[str]):
        try:
            chat_id = int(args[1])
        except ValueError:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID')
            return

        response = self._get_response(chat_id)
        self.messenger.reply(message, response)

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        if message.chat_id < 0:
            if len(args) == 1:
                response = self._get_response(message.chat_id)
                self.messenger.reply(message, response)
            elif len(args) == 2:
                self._parse_args_and_send(message, args)
            return

        if message.from_user is None:
            logger.error('Empty from_user in /stat command.', message_id=message.message_id, chat_id=message.chat_id)
            return

        if not self.users_repo.is_admin(message.from_user.id):
            self.messenger.reply(message, 'Это нужно делать в общем чате.')
            return

        if len(args) != 2:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} [CHAT_ID]')
            return

        self._parse_args_and_send(message, args)


class StatsHandler(MessageHandler):
    def __init__(self, replies: dict[re.Pattern, str], chats_repo: ChatsRepository, messenger: Messenger):
        self.replies = replies
        self.chats_repo = chats_repo
        self.messenger = messenger

    @staticmethod
    def new(replies: dict[str, str], chats_repo: ChatsRepository, messenger: Messenger) -> StatsHandler:
        replies_regexes: dict[re.Pattern, str] = {}

        for key, value in replies.items():
            regexp = re.compile(key)
            replies_regexes[regexp] = value

        return StatsHandler(replies_regexes, chats_repo, messenger)

    @decorators.non_empty
    def handle(self, text: str, message: telegram.Message) -> bool:
        # pylint: disable=W0221
        # Because of the decorator
        for key, value in self.replies.items():
            if key.search(text.lower()) is None:
                continue

            response = value + ':\n'
            response += get_stat(message.chat_id, self.chats_repo)
            self.messenger.reply(message, response)

            return True

        return False
