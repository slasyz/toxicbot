import aiogram

from toxic.interfaces import CommandHandler
from toxic.modules.joker.content import Joker


class JokeCommand(CommandHandler):
    def __init__(self, joker: Joker):
        self.joker = joker

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]):
        joke_text, _ = await self.joker.get_random_joke()
        return [joke_text]
