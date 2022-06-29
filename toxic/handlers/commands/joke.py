import aiogram

from toxic.handlers.handler import CommandHandler
from toxic.features.joke import Joker


class JokeCommand(CommandHandler):
    def __init__(self, joker: Joker):
        self.joker = joker

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]):
        joke_text, _ = await self.joker.get_random_joke()
        return [joke_text]
