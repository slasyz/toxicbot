from typing import List

import telegram

from toxicbot.handlers.commands.command import Command
from toxicbot.helpers import messages
from toxicbot.features.joke import Joker


class JokeCommand(Command):
    def __init__(self, joker: Joker):
        self.joker = joker

    def handle(self, message: telegram.Message, args: List[str]):
        text, _ = self.joker.get_random_joke()
        messages.reply(message, text)
