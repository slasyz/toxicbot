import telegram

from toxic.handlers.commands.command import Command
from toxic.features.joke import Joker
from toxic.messenger.messenger import Messenger


class JokeCommand(Command):
    def __init__(self, joker: Joker, messenger: Messenger):
        self.joker = joker
        self.messenger = messenger

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        joke_text, _ = self.joker.get_random_joke()
        self.messenger.reply(message, joke_text)
