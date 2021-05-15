import telegram

from toxicbot.handlers.commands.command import Command
from toxicbot.features.joke import Joker
from toxicbot.helpers.messages import Bot


class JokeCommand(Command):
    def __init__(self, joker: Joker, bot: Bot):
        self.joker = joker
        self.bot = bot

    def handle(self, message: telegram.Message, args: list[str]):
        text, _ = self.joker.get_random_joke()
        self.bot.reply(message, text)
