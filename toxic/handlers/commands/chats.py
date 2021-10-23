import telegram

from toxic.handlers.commands.command import Command
from toxic.messenger.messenger import Messenger
from toxic.repositories.chats import ChatsRepository


class ChatsCommand(Command):
    def __init__(self, chats_repo: ChatsRepository, messenger: Messenger):
        self.chats_repo = chats_repo
        self.messenger = messenger

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        response = []

        for id, title in self.chats_repo.list():
            response.append(f'{title} — #{id}')

        self.messenger.reply(message, '\n'.join(response))
