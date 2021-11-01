import telegram

from toxic.handlers.handler import CommandHandler
from toxic.messenger.messenger import Messenger
from toxic.repositories.chats import ChatsRepository


class ChatsCommand(CommandHandler):
    def __init__(self, chats_repo: ChatsRepository, messenger: Messenger):
        self.chats_repo = chats_repo
        self.messenger = messenger

    @staticmethod
    def is_admins_only() -> bool:
        return True

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        response = []

        for id, title in self.chats_repo.list():
            response.append(f'{title} — #{id}')

        self.messenger.reply(message, '\n'.join(response))
