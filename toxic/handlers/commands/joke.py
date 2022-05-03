import telegram

from toxic.handlers.handler import CommandHandler
from toxic.features.joke import Joker


class JokeCommand(CommandHandler):
    def __init__(self, joker: Joker):
        self.joker = joker

    async def handle(self, text: str, message: telegram.Message, args: list[str]):
        joke_text, _ = self.joker.get_random_joke()
        return [joke_text]
