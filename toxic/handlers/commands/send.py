import re

import telegram

from toxic.handlers.handler import CommandHandler
from toxic.messenger.messenger import Messenger
from toxic.repositories.chats import ChatsRepository


class SendCommand(CommandHandler):
    def __init__(self, chats_repository: ChatsRepository, messenger: Messenger):
        self.chats_repository = chats_repository
        self.messenger = messenger

    @staticmethod
    def is_admins_only() -> bool:
        return True

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        if len(args) < 3:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        try:
            chat_id = int(args[1])
        except ValueError:
            self.messenger.reply(message, f'Нужно писать так: /{args[0]} CHAT_ID MESSAGE')
            return

        if not self.chats_repository.is_existing(chat_id):
            self.messenger.reply(message, f'Не могу найти такой чат ({chat_id}).')
            return

        prefix_regexp = re.compile(r'^/' + args[0] + r'\s+' + args[1] + r'\s+')
        text = prefix_regexp.sub('', text)
        self.messenger.send(chat_id, text)
