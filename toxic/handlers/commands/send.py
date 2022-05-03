import re

import telegram

from toxic.handlers.handler import CommandHandler
from toxic.messenger.message import Message
from toxic.messenger.messenger import Messenger
from toxic.repositories.chats import ChatsRepository


class SendCommand(CommandHandler):
    def __init__(self, chats_repository: ChatsRepository, messenger: Messenger):
        self.chats_repository = chats_repository
        self.messenger = messenger

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, text: str, message: telegram.Message, args: list[str]) -> str | list[Message] | None:
        if len(args) < 3:
            return f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE'

        try:
            chat_id = int(args[1])
        except ValueError:
            return f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE'

        if not self.chats_repository.is_existing(chat_id):
            return f'Не могу найти такой чат ({chat_id}).'

        prefix_regexp = re.compile(r'^/' + args[0] + r'\s+' + args[1] + r'\s+')
        text = prefix_regexp.sub('', text)
        await self.messenger.send(chat_id, text)
        return 'Готово.'
