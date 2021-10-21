import telegram

from toxic.handlers.commands.command import Command
from toxic.features.joke import Joker
from toxic.messenger.messenger import Messenger


class JokeCommand(Command):
    def __init__(self, joker: Joker, messenger: Messenger):
        self.joker = joker
        self.messenger = messenger

    def handle(self, message: telegram.Message, args: list[str]):
        text, _ = self.joker.get_random_joke()
        self.messenger.reply(message, text)
